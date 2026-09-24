from django.contrib import admin
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from usuarios.admin import UsuarioAdmin
from usuarios.models import Usuario
from usuarios.repositories import UsuarioRepository
from usuarios.services import UsuarioService


class UsuarioAdminTests(TestCase):
    """Verifica que el administrador use solo los campos de dominio."""

    def setUp(self):
        self.request = RequestFactory().get('/admin/usuarios/usuario/')
        self.request.user = Usuario.objects.create_superuser(
            correo='superadmin@example.com',
            username='superadmin',
            nombre='Superadministrador',
            password='AdminPass123',
        )

    def test_form_hides_inherited_duplicate_identity_fields(self):
        """Oculta nombre, apellido y correo heredados de AbstractUser."""
        model_admin = UsuarioAdmin(Usuario, admin.site)

        form_fields = model_admin.get_form(request=self.request).base_fields

        self.assertNotIn('first_name', form_fields)
        self.assertNotIn('last_name', form_fields)
        self.assertNotIn('email', form_fields)
        self.assertIn('nombre', form_fields)
        self.assertIn('apellido', form_fields)
        self.assertIn('correo', form_fields)


class UsuarioRepositoryServiceTests(TestCase):
    """Verifica acceso a datos y reglas de negocio de usuarios."""

    def setUp(self):
        self.repository = UsuarioRepository()
        self.service = UsuarioService()
        self.admin = self.repository.create_user(
            correo='admin@example.com',
            username='admin',
            nombre='Ada',
            apellido='Admin',
            password='AdminPass123',
            rol='admin',
        )

    def test_create_user_hashes_password(self):
        """Almacena la contraseña cifrada y conserva los datos de dominio."""
        user = self.repository.create_user(
            correo='tecnico@example.com',
            username='tecnico',
            nombre='Tomás',
            apellido='Técnico',
            password='SecurePass123',
            rol='tecnico',
        )

        self.assertTrue(user.check_password('SecurePass123'))
        self.assertNotEqual(user.password, 'SecurePass123')
        self.assertEqual(user.rol, 'tecnico')

    def test_create_google_user_resolves_username_collision(self):
        """Genera un username incremental cuando el prefijo ya está ocupado."""
        self.repository.create_user(
            correo='juan.original@example.com',
            username='juan',
            nombre='Juan',
            rol='usuario',
        )

        first = self.service.create_google_user('juan@example.com', 'Juan Uno')
        second = self.service.create_google_user('juan@another.com', 'Juan Dos')

        self.assertEqual(first.username, 'juan1')
        self.assertEqual(second.username, 'juan2')
        self.assertFalse(first.has_usable_password())

    def test_service_rejects_duplicate_email(self):
        """Impide crear cuentas con correo repetido ignorando mayúsculas."""
        with self.assertRaisesMessage(Exception, 'Ya existe un usuario'):
            self.service.create(
                {
                    'correo': 'ADMIN@example.com',
                    'username': 'other-admin',
                    'nombre': 'Otra',
                    'rol': 'admin',
                },
                actor=self.admin,
            )

    def test_tecnico_lists_all_users_in_scope(self):
        """Permite al técnico listar todas las cuentas dentro de su alcance en modo lectura."""
        tecnico = self.repository.create_user(
            correo='tecnico@example.com',
            username='tecnico',
            nombre='Tania',
            rol='tecnico',
        )
        self.repository.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            rol='docente',
        )

        result = self.service.listar(actor=tecnico)

        self.assertEqual(result.count(), 3)

    def test_delete_deactivates_instead_of_removing(self):
        """Conserva la cuenta y cambia su estado al desactivarla."""
        user = self.repository.create_user(
            correo='inactive@example.com',
            username='inactive',
            nombre='Inés',
            rol='docente',
        )

        self.service.delete(user.id, actor=self.admin)
        user.refresh_from_db()

        self.assertFalse(user.is_active)
        self.assertTrue(Usuario.objects.filter(id=user.id).exists())


class UsuarioAPITests(APITestCase):
    """Comprueba contrato HTTP, seguridad y serialización de usuarios."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin@example.com',
            username='admin',
            nombre='Ada',
            apellido='Admin',
            password='AdminPass123',
            rol='admin',
        )
        self.tecnico = Usuario.objects.create_user(
            correo='tecnico@example.com',
            username='tecnico',
            nombre='Tomás',
            apellido='Técnico',
            password='TechPass123',
            rol='tecnico',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            apellido='Docente',
            password='TeacherPass123',
            rol='docente',
        )
        self.list_url = reverse('usuario-list')

    def test_requires_authentication(self):
        """Rechaza consultas de usuarios sin una sesión válida."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 401)

    def test_admin_lists_users_without_sensitive_fields(self):
        """Pagina usuarios sin exponer contraseñas."""
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        self.assertNotIn('password', response.data['results'][0])
        self.assertIn('nombre_completo', response.data['results'][0])

    def test_admin_creates_user_and_hashes_password(self):
        """Crea una cuenta válida mediante el endpoint protegido."""
        from espacios.models import Local
        local = Local.objects.create(
            codigo='LOC-CREATE',
            nombre='Sede de creación',
            ciudad='Huánuco',
        )
        self.client.force_authenticate(self.admin)
        payload = {
            'username': 'docente2',
            'correo': 'docente2@example.com',
            'nombre': 'Diego',
            'apellido': 'Docente',
            'dni': '12345678',
            'rol': 'docente',
            'password': 'TeacherPass456',
            'is_active': True,
            'sede_ids': [local.id],
            'sede_principal_id': local.id,
        }

        response = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(response.status_code, 201)
        created = Usuario.objects.get(correo='docente2@example.com')
        self.assertTrue(created.check_password('TeacherPass456'))
        self.assertIsNone(created.supervisor_id)
        self.assertTrue(created.usuario_sedes.filter(local_id=local.id).exists())
        self.assertNotIn('password', response.data)

    def test_create_requires_a_physical_location(self):
        """Impide crear cuentas institucionales sin una sede asignada."""
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            {
                'username': 'sin_sede',
                'correo': 'sin_sede@example.com',
                'nombre': 'Sin sede',
                'rol': 'docente',
                'password': 'TeacherPass456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('sede_ids', response.data['errores'])

    def test_duplicate_email_returns_field_error(self):
        """Reporta un correo duplicado con respuesta 400."""
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.list_url,
            {
                'username': 'duplicado',
                'correo': 'ADMIN@example.com',
                'nombre': 'Duplicado',
                'rol': 'admin',
                'password': 'DuplicatePass123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('correo', response.data['errores'])

    def test_tecnico_cannot_create_or_edit_users(self):
        """Comprueba que el técnico tiene acceso de solo lectura y no puede crear ni editar usuarios."""
        self.client.force_authenticate(self.tecnico)

        list_response = self.client.get(self.list_url)
        create_response = self.client.post(
            self.list_url,
            {
                'username': 'forbidden-user',
                'correo': 'forbidden@example.com',
                'nombre': 'Prohibido',
                'rol': 'docente',
                'password': 'ForbiddenPass123',
            },
            format='json',
        )
        patch_response = self.client.patch(
            reverse('usuario-detail', args=[self.docente.id]),
            {'nombre': 'Nombre Editado'},
            format='json',
        )
        delete_response = self.client.delete(
            reverse('usuario-detail', args=[self.docente.id]),
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(patch_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)

    def test_filters_and_statistics(self):
        """Entrega resultados filtrados e indicadores consistentes."""
        self.client.force_authenticate(self.admin)

        filtered = self.client.get(self.list_url, {'search': 'Diana'})
        stats = self.client.get(reverse('usuario-estadisticas'))

        self.assertEqual(filtered.data['count'], 1)
        self.assertEqual(filtered.data['results'][0]['id'], self.docente.id)
        self.assertEqual(stats.status_code, 200)
        self.assertEqual(stats.data['total'], 3)
        self.assertEqual(stats.data['docentes'], 1)

    def test_tecnico_statistics_include_all_in_scope(self):
        """Expone al técnico métricas del personal dentro de su alcance territorial."""
        self.client.force_authenticate(self.tecnico)

        response = self.client.get(reverse('usuario-estadisticas'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 3)

    def test_delete_soft_deactivates_user(self):
        """Desactiva la cuenta desde la API sin eliminar el registro."""
        self.client.force_authenticate(self.admin)

        response = self.client.delete(
            reverse('usuario-detail', args=[self.docente.id])
        )
        self.docente.refresh_from_db()

        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.docente.is_active)

    def test_crear_usuario_con_supervisor_y_sedes(self):
        """Valida que se pueda asignar supervisor y sedes al crear un usuario."""
        from espacios.models import Local
        local = Local.objects.create(codigo='LOC-TEST', nombre='Sede Huánuco', ciudad='Huánuco')
        self.client.force_authenticate(self.admin)

        payload = {
            'username': 'tecnico_hco',
            'correo': 'tecnico_hco@example.com',
            'nombre': 'Carlos',
            'apellido': 'Técnico',
            'rol': 'tecnico',
            'supervisor_id': self.admin.id,
            'sede_ids': [local.id],
            'password': 'Password123',
            'is_active': True,
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        created_id = response.data['id']
        created = Usuario.objects.get(id=created_id)
        self.assertEqual(created.supervisor_id, self.admin.id)
        self.assertTrue(created.usuario_sedes.filter(local_id=local.id).exists())

    def test_validacion_supervisor_circular_rechazada(self):
        """Impide relaciones jerárquicas circulares."""
        from rest_framework.exceptions import ValidationError
        service = UsuarioService()
        sub = Usuario.objects.create_user(
            correo='sub@example.com',
            username='sub',
            nombre='Subordinado',
            supervisor=self.admin,
        )
        with self.assertRaises(ValidationError):
            service.update(self.admin.id, {'supervisor_id': sub.id})

    def test_responsable_solo_gestiona_personal_directamente_a_su_cargo(self):
        """Limita edición y desactivación del responsable a sus subordinados directos."""
        repository = UsuarioRepository()
        service = UsuarioService()
        responsable = repository.create_user(
            correo='responsable@example.com',
            username='responsable',
            nombre='Rosa',
            rol='responsable',
        )
        tecnico_a_cargo = repository.create_user(
            correo='tecnico-cargo@example.com',
            username='tecnico-cargo',
            nombre='Técnico a cargo',
            rol='tecnico',
            supervisor=responsable,
        )
        tecnico_fuera = repository.create_user(
            correo='tecnico-fuera@example.com',
            username='tecnico-fuera',
            nombre='Técnico fuera',
            rol='tecnico',
            supervisor=self.admin,
        )

        service.update(tecnico_a_cargo.id, {'nombre': 'Técnico actualizado'}, actor=responsable)
        with self.assertRaisesMessage(Exception, 'directamente a tu cargo'):
            service.update(tecnico_fuera.id, {'nombre': 'No permitido'}, actor=responsable)
        with self.assertRaisesMessage(Exception, 'directamente a tu cargo'):
            service.delete(tecnico_fuera.id, actor=responsable)

    def test_permisos_personalizados_override(self):
        """Comprueba que un permiso personalizado tiene precedencia sobre el rol base."""
        # Un técnico por defecto no puede eliminar equipos
        self.assertFalse(self.tecnico.tiene_permiso('equipos', 'eliminar'))
        # Personalizar permiso para permitir eliminar equipos
        from usuarios.models import PermisoPersonalizado
        PermisoPersonalizado.objects.create(
            usuario=self.tecnico,
            modulo='equipos',
            accion='eliminar',
            permitido=True,
        )
        self.assertTrue(self.tecnico.tiene_permiso('equipos', 'eliminar'))

    def test_endpoint_organigrama_estructura(self):
        """Valida que los docentes sean nodos independientes del organigrama."""
        self.docente.supervisor = self.admin
        self.docente.save()
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse('usuario-organigrama'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('arbol', response.data)
        arbol = response.data['arbol']
        # Los docentes no deben colgar de ningún supervisor aunque exista una
        # relación heredada en la base de datos.
        docente_root = next((n for n in arbol if n['id'] == self.docente.id), None)
        self.assertIsNotNone(docente_root)
        self.assertIsNone(docente_root['supervisor_id'])

        # Buscar el nodo admin en las raíces
        admin_node = next((n for n in arbol if n['id'] == self.admin.id), None)
        self.assertIsNotNone(admin_node)
        self.assertNotIn(self.docente.id, [child['id'] for child in admin_node['children']])

        subordinados_response = self.client.get(
            reverse('usuario-subordinados', args=[self.admin.id]),
        )
        self.assertEqual(subordinados_response.status_code, 200)
        self.assertNotIn(self.docente.id, [item['id'] for item in subordinados_response.data])

    def test_organigrama_global_usa_todas_las_sedes_permitidas(self):
        """La vista global no debe reducirse a la primera sede del administrador."""
        from espacios.models import Local
        from usuarios.models import UsuarioSede

        sede_central = Local.objects.create(
            codigo='LOC-CENTRAL',
            nombre='Campus Central',
            ciudad='Huánuco',
        )
        sede_esperanza = Local.objects.create(
            codigo='LOC-ESPERANZA',
            nombre='Sede La Esperanza',
            ciudad='Huánuco',
        )
        UsuarioSede.objects.create(
            usuario=self.admin,
            local=sede_central,
            activo=True,
            es_sede_principal=True,
        )
        UsuarioSede.objects.create(
            usuario=self.admin,
            local=sede_esperanza,
            activo=True,
        )
        usuario_central = Usuario.objects.create_user(
            correo='usuario-central@example.com',
            username='usuario-central',
            nombre='Usuario Central',
            rol='usuario',
        )
        usuario_esperanza = Usuario.objects.create_user(
            correo='usuario-esperanza@example.com',
            username='usuario-esperanza',
            nombre='Usuario Esperanza',
            rol='usuario',
        )
        UsuarioSede.objects.create(usuario=usuario_central, local=sede_central, activo=True)
        UsuarioSede.objects.create(usuario=usuario_esperanza, local=sede_esperanza, activo=True)

        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('usuario-organigrama'))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['sede'])

        def collect_ids(nodes):
            ids = []
            for node in nodes:
                ids.append(node['id'])
                ids.extend(collect_ids(node.get('children', [])))
            return ids

        ids = collect_ids(response.data['arbol'])
        self.assertIn(usuario_central.id, ids)
        self.assertIn(usuario_esperanza.id, ids)

    def test_organigrama_meta_y_grupos(self):
        """Valida que el organigrama incluya de forma aditiva meta y grupos funcionales con ordenamiento correcto."""
        tecnico = Usuario.objects.create_user(
            correo='tecnico-jerarquia@example.com',
            username='tecnico-jerarquia',
            nombre='Tecnico Jerarquico',
            rol='tecnico',
            supervisor=self.admin,
        )
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('usuario-organigrama'))
        self.assertEqual(response.status_code, 200)

        # 1. Comprobar que arbol existe y contiene raíces
        self.assertIn('arbol', response.data)
        arbol = response.data['arbol']
        self.assertTrue(len(arbol) > 0)

        # 2. Comprobar que las raíces con descendientes vienen primero
        admin_idx = next(i for i, n in enumerate(arbol) if n['id'] == self.admin.id)
        docente_idx = next(i for i, n in enumerate(arbol) if n['id'] == self.docente.id)
        self.assertLess(admin_idx, docente_idx)

        # 3. Comprobar meta aditiva
        self.assertIn('meta', response.data)
        meta = response.data['meta']
        self.assertIn('total', meta)
        self.assertIn('total_mando', meta)
        self.assertIn('total_sin_supervisor', meta)
        self.assertIn('total_docentes', meta)
        self.assertIn('total_sin_sede', meta)
        self.assertGreaterEqual(meta['total_mando'], 2)
        self.assertGreaterEqual(meta['total_docentes'], 1)

        # 4. Comprobar grupos aditivos
        self.assertIn('grupos', response.data)
        grupos = response.data['grupos']
        self.assertIn('arbol_mando', grupos)
        self.assertIn('sin_supervisor', grupos)
        self.assertIn('docentes', grupos)
        self.assertIn('sin_sede', grupos)
        self.assertTrue(any(n['id'] == self.admin.id for n in grupos['arbol_mando']))
        self.assertTrue(any(n['id'] == self.docente.id for n in grupos['docentes']))

    def test_endpoint_permisos_y_actividad(self):
        """Consulta y actualiza la matriz de permisos y el historial de actividad."""
        self.client.force_authenticate(self.admin)
        permisos_url = reverse('usuario-permisos', args=[self.docente.id])
        actividad_url = reverse('usuario-actividad', args=[self.docente.id])

        # Consultar permisos
        get_res = self.client.get(permisos_url)
        self.assertEqual(get_res.status_code, 200)
        self.assertIn('permisos_base', get_res.data)
        self.assertIn('permisos_efectivos', get_res.data)

        # Modificar permisos
        post_res = self.client.post(
            permisos_url,
            {'permisos': [{'modulo': 'espacios', 'accion': 'crear', 'permitido': True}]},
            format='json',
        )
        self.assertEqual(post_res.status_code, 200)
        self.assertTrue(post_res.data['permisos_efectivos']['espacios']['crear'])

        # Restablecer permisos
        reset_res = self.client.post(permisos_url, {'reset_to_default': True}, format='json')
        self.assertEqual(reset_res.status_code, 200)
        self.assertFalse(reset_res.data['permisos_efectivos']['espacios']['crear'])

        # Consultar actividad
        act_res = self.client.get(actividad_url)
        self.assertEqual(act_res.status_code, 200)
        self.assertIsInstance(act_res.data, list)

    def test_admin_no_puede_asignar_supervisor_de_otra_sede(self):
        """Impide a un administrador asignar un supervisor perteneciente a otra sede."""
        from espacios.models import Local
        from usuarios.models import UsuarioSede
        local_hco = Local.objects.create(codigo='LOC-HCO', nombre='Huánuco', ciudad='Huánuco')
        local_tm = Local.objects.create(codigo='LOC-TM', nombre='Tingo María', ciudad='Tingo María')

        # Asignar sede Huánuco a admin
        UsuarioSede.objects.create(usuario=self.admin, local=local_hco, activo=True, es_sede_principal=True)

        # Crear supervisor en Tingo María
        sup_tingo = Usuario.objects.create_user(
            correo='sup_tingo@example.com',
            username='sup_tingo',
            nombre='Supervisor Tingo',
            rol='admin',
        )
        UsuarioSede.objects.create(usuario=sup_tingo, local=local_tm, activo=True, es_sede_principal=True)

        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.list_url,
            {
                'username': 'nuevo_user',
                'correo': 'nuevo_user@example.com',
                'nombre': 'Nuevo',
                'rol': 'tecnico',
                'supervisor_id': sup_tingo.id,
                'sede_ids': [local_hco.id],
                'password': 'Password123',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('supervisor_id', response.data['errores'])

    def test_admin_no_puede_modificar_usuario_otra_sede(self):
        """Impide a un administrador editar un usuario de una sede a la que no pertenece."""
        from espacios.models import Local
        from usuarios.models import UsuarioSede
        local_hco = Local.objects.create(codigo='LOC-HCO2', nombre='Huánuco 2', ciudad='Huánuco')
        local_tm = Local.objects.create(codigo='LOC-TM2', nombre='Tingo María 2', ciudad='Tingo María')

        UsuarioSede.objects.create(usuario=self.admin, local=local_hco, activo=True, es_sede_principal=True)

        user_tm = Usuario.objects.create_user(
            correo='user_tm@example.com',
            username='user_tm',
            nombre='Usuario Tingo',
            rol='docente',
        )
        UsuarioSede.objects.create(usuario=user_tm, local=local_tm, activo=True, es_sede_principal=True)

        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            reverse('usuario-detail', args=[user_tm.id]),
            {'nombre': 'Nombre Hackeado'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_no_puede_listar_otra_sede(self):
        """Rechaza que un administrador consulte con local_id de otra sede física."""
        from espacios.models import Local
        from usuarios.models import UsuarioSede
        local_hco = Local.objects.create(codigo='LOC-HCO3', nombre='Huánuco 3', ciudad='Huánuco')
        local_tm = Local.objects.create(codigo='LOC-TM3', nombre='Tingo María 3', ciudad='Tingo María')

        UsuarioSede.objects.create(usuario=self.admin, local=local_hco, activo=True, es_sede_principal=True)

        self.client.force_authenticate(self.admin)
        response = self.client.get(self.list_url, {'local_id': local_tm.id})
        self.assertEqual(response.status_code, 400)

    def test_tecnico_no_puede_ver_actividad_o_permisos(self):
        """Bloquea al técnico el acceso a permisos y auditoría de cuentas superiores."""
        self.client.force_authenticate(self.tecnico)

        res_permisos = self.client.get(reverse('usuario-permisos', args=[self.admin.id]))
        self.assertEqual(res_permisos.status_code, 403)

        res_actividad = self.client.get(reverse('usuario-actividad', args=[self.admin.id]))
        self.assertEqual(res_actividad.status_code, 403)

    def test_responsable_permiso_espacios_y_override(self):
        """Comprueba que un responsable puede gestionar espacios y que la matriz modular se aplica en API."""
        from espacios.models import Espacio, Local, Edificio
        from usuarios.models import PermisoPersonalizado

        local = Local.objects.create(codigo='LOC-RESP', nombre='Sede Esperanza', ciudad='Huánuco')
        edificio = Edificio.objects.create(codigo='ED-RESP', nombre='Pabellón E', local=local)

        responsable = Usuario.objects.create_user(
            correo='responsable.esp@example.com',
            username='respesp',
            nombre='Renato',
            rol='responsable',
            password='Password123',
        )

        self.client.force_authenticate(responsable)

        # 1. Responsable puede crear espacios por defecto (en ROL_PERMISOS_BASE)
        create_res = self.client.post(
            reverse('espacio-list'),
            {
                'codigo_espacio': 'LAB-RESP-1',
                'tipo': 'laboratorio',
                'edificio_id': edificio.id,
                'pabellon': edificio.nombre,
                'piso': '1',
                'activo': True,
            },
            format='json',
        )
        self.assertEqual(create_res.status_code, 201)
        espacio_id = create_res.data['id']

        # 2. Revocar permiso de eliminación al responsable mediante PermisoPersonalizado
        PermisoPersonalizado.objects.create(
            usuario=responsable,
            modulo='espacios',
            accion='eliminar',
            permitido=False,
        )

        # 3. Intentar eliminar: debe responder 403 Forbidden debido al permiso modular
        del_res = self.client.delete(reverse('espacio-detail', args=[espacio_id]))
        self.assertEqual(del_res.status_code, 403)


class RolPermisosBaseTests(TestCase):
    """Verifica que la matriz ROL_PERMISOS_BASE cumpla la especificacion para cada perfil."""

    def test_docente_permisos_base(self):
        """Docente solo tiene acceso a software e incidencias, con ver=False en espacios y equipos."""
        docente = Usuario.objects.create_user(
            correo='ana.docente@example.com',
            username='ana.docente',
            nombre='Ana',
            rol='docente',
        )
        permisos = docente.get_permisos_efectivos()

        self.assertFalse(permisos['espacios']['ver'])
        self.assertFalse(permisos['equipos']['ver'])
        self.assertFalse(permisos['mantenimiento']['ver'])
        self.assertFalse(permisos['usuarios']['ver'])
        self.assertFalse(permisos['auditoria']['ver'])

        self.assertTrue(permisos['software']['ver'])
        self.assertFalse(permisos['software']['crear'])

        self.assertTrue(permisos['incidencias']['ver'])
        self.assertTrue(permisos['incidencias']['crear'])
        self.assertFalse(permisos['incidencias']['editar'])
        self.assertFalse(permisos['incidencias']['eliminar'])

    def test_usuario_permisos_base(self):
        """Usuario regular solo tiene acceso a software e incidencias."""
        usuario = Usuario.objects.create_user(
            correo='usuario.regular@example.com',
            username='usuario.regular',
            nombre='Carlos',
            rol='usuario',
        )
        permisos = usuario.get_permisos_efectivos()

        self.assertFalse(permisos['espacios']['ver'])
        self.assertFalse(permisos['equipos']['ver'])
        self.assertFalse(permisos['mantenimiento']['ver'])
        self.assertFalse(permisos['usuarios']['ver'])
        self.assertFalse(permisos['auditoria']['ver'])

        self.assertTrue(permisos['software']['ver'])
        self.assertTrue(permisos['incidencias']['ver'])
        self.assertTrue(permisos['incidencias']['crear'])
        self.assertFalse(permisos['incidencias']['editar'])

    def test_tecnico_permisos_base(self):
        """Tecnico mantiene ver/crear/editar en hardware, incidencias, mantenimiento y software."""
        tecnico = Usuario.objects.create_user(
            correo='tecnico.base@example.com',
            username='tecnico.base',
            nombre='Tomás',
            rol='tecnico',
        )
        permisos = tecnico.get_permisos_efectivos()

        self.assertTrue(permisos['espacios']['ver'])
        self.assertFalse(permisos['espacios']['crear'])

        self.assertTrue(permisos['usuarios']['ver'])
        self.assertFalse(permisos['usuarios']['crear'])
        self.assertFalse(permisos['usuarios']['editar'])
        self.assertFalse(permisos['usuarios']['eliminar'])

        for mod in ('equipos', 'mantenimiento', 'incidencias', 'software'):
            self.assertTrue(permisos[mod]['ver'])
            self.assertTrue(permisos[mod]['crear'])
            self.assertTrue(permisos[mod]['editar'])
            self.assertFalse(permisos[mod]['eliminar'])

    def test_responsable_permisos_base(self):
        """Responsable mantiene gestion en espacios, equipos, mantenimiento, incidencias, software y usuarios."""
        responsable = Usuario.objects.create_user(
            correo='responsable.base@example.com',
            username='responsable.base',
            nombre='Regina',
            rol='responsable',
        )
        permisos = responsable.get_permisos_efectivos()

        self.assertTrue(permisos['espacios']['ver'])
        self.assertTrue(permisos['espacios']['crear'])
        self.assertTrue(permisos['espacios']['editar'])
        self.assertTrue(permisos['espacios']['eliminar'])

        for mod in ('equipos', 'mantenimiento', 'software', 'usuarios'):
            self.assertTrue(permisos[mod]['ver'])
            self.assertTrue(permisos[mod]['crear'])
            self.assertTrue(permisos[mod]['editar'])
            self.assertFalse(permisos[mod]['eliminar'])

        self.assertTrue(permisos['incidencias']['ver'])
        self.assertTrue(permisos['incidencias']['crear'])
        self.assertTrue(permisos['incidencias']['editar'])
        self.assertTrue(permisos['incidencias']['eliminar'])

        self.assertTrue(permisos['auditoria']['ver'])
        self.assertFalse(permisos['auditoria']['crear'])

    def test_admin_y_superadmin_permisos_base(self):
        """Superadmin tiene acceso irrestricto y admin acceso total con solo lectura en auditoria."""
        superadmin = Usuario.objects.create_superuser(
            correo='super.base@example.com',
            username='super.base',
            nombre='Super',
            password='Password123',
        )
        super_permisos = superadmin.get_permisos_efectivos()
        for mod in ('espacios', 'equipos', 'mantenimiento', 'incidencias', 'software', 'usuarios', 'auditoria'):
            for acc in ('ver', 'crear', 'editar', 'eliminar'):
                self.assertTrue(super_permisos[mod][acc])

        admin = Usuario.objects.create_user(
            correo='admin.base@example.com',
            username='admin.base',
            nombre='Admin',
            rol='admin',
        )
        admin_permisos = admin.get_permisos_efectivos()
        for mod in ('espacios', 'equipos', 'mantenimiento', 'incidencias', 'software', 'usuarios'):
            for acc in ('ver', 'crear', 'editar', 'eliminar'):
                self.assertTrue(admin_permisos[mod][acc])
        self.assertTrue(admin_permisos['auditoria']['ver'])
        self.assertFalse(admin_permisos['auditoria']['crear'])


class DocenteAPIAccesoTests(APITestCase):
    """Verifica el control de acceso en endpoints API para el rol docente."""

    def setUp(self):
        self.docente = Usuario.objects.create_user(
            correo='ana.api@example.com',
            username='ana.api',
            nombre='Ana',
            password='DocentePass123',
            rol='docente',
        )
        self.client.force_authenticate(user=self.docente)

    def test_docente_bloqueado_en_espacios(self):
        """Docente recibe 403 Forbidden al intentar listar o crear espacios."""
        res_list = self.client.get(reverse('espacio-list'))
        self.assertEqual(res_list.status_code, 403)

        res_post = self.client.post(reverse('espacio-list'), {'nombre': 'Aula 101'})
        self.assertEqual(res_post.status_code, 403)

    def test_docente_bloqueado_en_equipos(self):
        """Docente recibe 403 Forbidden al intentar listar o crear equipos."""
        res_list = self.client.get(reverse('equipo-list'))
        self.assertEqual(res_list.status_code, 403)

        res_post = self.client.post(reverse('equipo-list'), {'codigo': 'PC-01'})
        self.assertEqual(res_post.status_code, 403)

    def test_docente_autorizado_en_software_solo_lectura(self):
        """Docente puede listar software pero no crear."""
        res_list = self.client.get(reverse('producto-software-list'))
        self.assertEqual(res_list.status_code, 200)

        res_post = self.client.post(reverse('producto-software-list'), {'nombre': 'LibreOffice'})
        self.assertEqual(res_post.status_code, 403)

    def test_docente_autorizado_en_incidencias(self):
        """Docente puede listar e interactuar con incidencias."""
        res_list = self.client.get(reverse('incidencia-list'))
        self.assertEqual(res_list.status_code, 200)
