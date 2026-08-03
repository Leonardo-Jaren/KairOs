from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from espacios.models import Espacio
from historial.models import Historial
from historial.repositories import HistorialRepository
from historial.services import HistorialService
from usuarios.models import Usuario
from usuarios.repositories import UsuarioRepository
from usuarios.services import UsuarioService
from espacios.services import EspacioService, EspacioUsuarioService


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------

class HistorialRepositoryTests(TestCase):
    """Verifica que el repositorio protege la inmutabilidad del log."""

    def setUp(self):
        self.repository = HistorialRepository()
        self.usuario = Usuario.objects.create_user(
            correo='actor@example.com',
            username='actor',
            nombre='Actor',
            rol='admin',
        )
        self.service = HistorialService()
        self.evento = self.service.registrar(
            objeto=self.usuario,
            tipo_evento='usuario.alta',
            descripcion='Cuenta actor registrada.',
            usuario=self.usuario,
        )

    def test_update_levanta_error(self):
        """Impide modificar un registro de auditoría existente."""
        with self.assertRaises(NotImplementedError):
            self.repository.update(self.evento, descripcion='modificado')

    def test_delete_levanta_error(self):
        """Impide eliminar un registro de auditoría."""
        with self.assertRaises(NotImplementedError):
            self.repository.delete(self.evento)

    def test_registrar_persiste_el_evento(self):
        """Crea un registro inmutable con todos los campos esperados."""
        self.assertEqual(Historial.objects.count(), 1)
        self.assertEqual(self.evento.tipo_evento, 'usuario.alta')
        self.assertEqual(self.evento.object_id, self.usuario.pk)
        self.assertEqual(self.evento.usuario, self.usuario)

    def test_listar_filtra_por_content_type(self):
        """Devuelve solo los eventos del tipo de objeto indicado."""
        otro_usuario = Usuario.objects.create_user(
            correo='otro@example.com',
            username='otro',
            nombre='Otro',
            rol='docente',
        )
        self.service.registrar(
            objeto=otro_usuario,
            tipo_evento='usuario.alta',
            descripcion='Cuenta otro registrada.',
        )

        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(Usuario)
        resultado = self.repository.listar(content_type_id=ct.id)

        self.assertEqual(resultado.count(), 2)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class HistorialServiceTests(TestCase):
    """Verifica el registro y consulta del log de auditoría global."""

    def setUp(self):
        self.service = HistorialService()
        self.actor = Usuario.objects.create_user(
            correo='admin@example.com',
            username='admin',
            nombre='Ada',
            rol='admin',
        )
        self.objeto = Usuario.objects.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            rol='docente',
        )

    def test_registrar_crea_evento_con_campos_correctos(self):
        """Almacena todos los campos del evento correctamente."""
        evento = self.service.registrar(
            objeto=self.objeto,
            tipo_evento='usuario.alta',
            descripcion='Cuenta docente registrada.',
            usuario=self.actor,
            datos_extra={'rol': 'docente'},
        )

        self.assertEqual(Historial.objects.count(), 1)
        self.assertEqual(evento.tipo_evento, 'usuario.alta')
        self.assertEqual(evento.object_id, self.objeto.pk)
        self.assertEqual(evento.usuario, self.actor)
        self.assertEqual(evento.descripcion, 'Cuenta docente registrada.')
        self.assertEqual(evento.datos_extra, {'rol': 'docente'})
        self.assertEqual(evento.content_type.model, 'usuario')

    def test_update_bloqueado(self):
        """No permite modificar eventos del log."""
        with self.assertRaises(NotImplementedError):
            self.service.update(1, {})

    def test_delete_bloqueado(self):
        """No permite eliminar eventos del log."""
        with self.assertRaises(NotImplementedError):
            self.service.delete(1)

    def test_listar_sin_filtros_retorna_todos(self):
        """Sin filtros retorna todos los eventos registrados."""
        self.service.registrar(objeto=self.objeto, tipo_evento='usuario.alta', descripcion='Alta.')
        self.service.registrar(objeto=self.actor, tipo_evento='usuario.alta', descripcion='Alta admin.')

        resultado = self.service.listar()

        self.assertEqual(resultado.count(), 2)

    def test_listar_por_modulo(self):
        """Filtra eventos por el nombre del modelo auditado."""
        self.service.registrar(objeto=self.objeto, tipo_evento='usuario.alta', descripcion='Alta.')
        espacio = Espacio.objects.create(
            codigo_espacio='LAB-001',
            tipo='laboratorio',
            pabellon='P1',
            piso='1',
        )
        self.service.registrar(objeto=espacio, tipo_evento='espacio.alta', descripcion='Alta espacio.')

        resultado = self.service.listar(modulo='usuario')

        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first().tipo_evento, 'usuario.alta')

    def test_listar_por_tipo_evento(self):
        """Filtra eventos cuyo tipo comienza con el prefijo indicado."""
        self.service.registrar(objeto=self.objeto, tipo_evento='usuario.alta', descripcion='Alta.')
        self.service.registrar(objeto=self.objeto, tipo_evento='usuario.desactivacion', descripcion='Baja.')

        resultado = self.service.listar(tipo_evento='usuario.alta')

        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first().tipo_evento, 'usuario.alta')

    def test_listar_por_object_id(self):
        """Devuelve solo los eventos del objeto con el ID indicado."""
        self.service.registrar(objeto=self.objeto, tipo_evento='usuario.alta', descripcion='Alta.')
        self.service.registrar(objeto=self.actor, tipo_evento='usuario.alta', descripcion='Alta admin.')

        resultado = self.service.listar(modulo='usuario', object_id=self.objeto.pk)

        self.assertEqual(resultado.count(), 1)
        self.assertEqual(resultado.first().object_id, self.objeto.pk)

    def test_get_by_id_retorna_evento(self):
        """Recupera un evento concreto por su ID."""
        evento = self.service.registrar(
            objeto=self.objeto,
            tipo_evento='usuario.alta',
            descripcion='Alta.',
        )

        recuperado = self.service.get_by_id(evento.id)

        self.assertEqual(recuperado.id, evento.id)

    def test_modulo_inexistente_retorna_lista_vacia(self):
        """Un nombre de módulo desconocido no lanza excepción — devuelve vacío."""
        self.service.registrar(objeto=self.objeto, tipo_evento='usuario.alta', descripcion='Alta.')

        resultado = self.service.listar(modulo='modeloinexistente')

        self.assertEqual(resultado.count(), 0)


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

class HistorialAPITests(APITestCase):
    """Comprueba que la API expone el log en modo estrictamente solo lectura."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin@example.com',
            username='admin',
            nombre='Ada',
            rol='admin',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            rol='docente',
        )
        self.service = HistorialService()
        self.evento = self.service.registrar(
            objeto=self.docente,
            tipo_evento='usuario.alta',
            descripcion='Cuenta docente registrada.',
            usuario=self.admin,
        )
        self.list_url = reverse('historial-list')

    def test_requiere_autenticacion(self):
        """Rechaza consultas sin credenciales con 401."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 401)

    def test_list_retorna_eventos_paginados(self):
        """Devuelve los eventos del log con paginación estándar."""
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 1)
        resultado = response.data['results'][0]
        self.assertEqual(resultado['tipo_evento'], 'usuario.alta')
        self.assertEqual(resultado['modulo'], 'usuario')
        self.assertIn('usuario_nombre', resultado)
        self.assertNotIn('content_type', resultado)

    def test_filtro_por_modulo(self):
        """Devuelve únicamente los eventos del módulo indicado."""
        espacio = Espacio.objects.create(
            codigo_espacio='LAB-001', tipo='laboratorio', pabellon='P1', piso='1'
        )
        self.service.registrar(objeto=espacio, tipo_evento='espacio.alta', descripcion='Alta.')
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.list_url, {'modulo': 'usuario'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['modulo'], 'usuario')

    def test_filtro_por_tipo_evento(self):
        """Filtra usando el prefijo del tipo de evento."""
        self.service.registrar(
            objeto=self.docente,
            tipo_evento='usuario.desactivacion',
            descripcion='Cuenta desactivada.',
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.list_url, {'tipo_evento': 'usuario.alta'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_retorna_evento_correcto(self):
        """Devuelve el detalle de un evento por su ID."""
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse('historial-detail', args=[self.evento.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.evento.id)
        self.assertEqual(response.data['tipo_evento'], 'usuario.alta')

    def test_post_no_permitido(self):
        """Rechaza intentos de crear eventos desde la API."""
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.list_url, {}, format='json')

        self.assertEqual(response.status_code, 405)

    def test_put_no_permitido(self):
        """Rechaza intentos de modificar eventos desde la API."""
        self.client.force_authenticate(self.admin)

        response = self.client.put(
            reverse('historial-detail', args=[self.evento.id]), {}, format='json'
        )

        self.assertEqual(response.status_code, 405)

    def test_delete_no_permitido(self):
        """Rechaza intentos de eliminar eventos desde la API."""
        self.client.force_authenticate(self.admin)

        response = self.client.delete(
            reverse('historial-detail', args=[self.evento.id])
        )

        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# Integración — UsuarioService
# ---------------------------------------------------------------------------

class HistorialIntegracionUsuarioTests(TestCase):
    """Verifica que UsuarioService emite los eventos correctos al historial."""

    def setUp(self):
        self.repo = UsuarioRepository()
        self.service = UsuarioService()
        self.admin = self.repo.create_user(
            correo='admin@example.com',
            username='admin',
            nombre='Ada',
            rol='admin',
            password='AdminPass123',
        )

    def test_crear_usuario_registra_evento_alta(self):
        """Crear una cuenta genera un evento usuario.alta en el historial."""
        self.service.create(
            {
                'correo': 'docente@example.com',
                'username': 'docente',
                'nombre': 'Diana',
                'apellido': 'Docente',
                'rol': 'docente',
                'password': 'Pass123456',
            },
            actor=self.admin,
        )

        self.assertEqual(Historial.objects.count(), 1)
        evento = Historial.objects.first()
        self.assertEqual(evento.tipo_evento, UsuarioService.ALTA)
        self.assertEqual(evento.usuario, self.admin)

    def test_desactivar_usuario_registra_evento_desactivacion(self):
        """Desactivar una cuenta genera un evento usuario.desactivacion."""
        docente = self.repo.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            rol='docente',
        )

        self.service.delete(docente.id, actor=self.admin)

        self.assertEqual(Historial.objects.count(), 1)
        evento = Historial.objects.first()
        self.assertEqual(evento.tipo_evento, UsuarioService.DESACTIVACION)
        self.assertEqual(evento.object_id, docente.pk)

    def test_cambio_rol_registra_evento_con_datos_extra(self):
        """Modificar el rol genera un evento con el cambio documentado."""
        docente = self.repo.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            rol='docente',
        )

        self.service.update(
            docente.id,
            {'rol': 'tecnico'},
            actor=self.admin,
        )

        self.assertEqual(Historial.objects.count(), 1)
        evento = Historial.objects.first()
        self.assertEqual(evento.tipo_evento, UsuarioService.CAMBIO_ROL)
        cambio = evento.datos_extra['cambios'][0]
        self.assertEqual(cambio['campo'], 'Rol')
        self.assertEqual(cambio['antes'], 'docente')
        self.assertEqual(cambio['despues'], 'tecnico')

    def test_update_campo_no_rol_genera_evento_actualizacion(self):
        """Actualizar cualquier campo (no solo rol) genera un evento de auditoría."""
        docente = self.repo.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            rol='docente',
        )

        self.service.update(
            docente.id,
            {'nombre': 'Diana Actualizada'},
            actor=self.admin,
        )

        self.assertEqual(Historial.objects.count(), 1)
        evento = Historial.objects.first()
        self.assertEqual(evento.tipo_evento, 'usuario.actualizacion')
        cambios = evento.datos_extra['cambios']
        self.assertTrue(any(c['campo'] == 'Nombre completo' for c in cambios))


# ---------------------------------------------------------------------------
# Integración — EspacioService
# ---------------------------------------------------------------------------

class HistorialIntegracionEspacioTests(TestCase):
    """Verifica que EspacioService emite los eventos correctos al historial."""

    PAYLOAD_ESPACIO = {
        'codigo_espacio': 'LAB-301',
        'tipo': 'laboratorio',
        'pabellon': 'Pabellón 3',
        'piso': '3',
    }

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin@example.com',
            username='admin',
            nombre='Ada',
            rol='admin',
        )
        self.service = EspacioService()

    def test_crear_espacio_registra_evento_alta(self):
        """Crear un espacio genera un evento espacio.alta en el historial."""
        self.service.create(self.PAYLOAD_ESPACIO, actor=self.admin)

        self.assertEqual(Historial.objects.count(), 1)
        evento = Historial.objects.first()
        self.assertEqual(evento.tipo_evento, EspacioService.ALTA)
        self.assertEqual(evento.usuario, self.admin)

    def test_desactivar_espacio_registra_evento_desactivacion(self):
        """Desactivar un espacio genera un evento espacio.desactivacion."""
        espacio = self.service.create(self.PAYLOAD_ESPACIO, actor=self.admin)
        Historial.objects.all().delete()

        self.service.delete(espacio.id, actor=self.admin)

        self.assertEqual(Historial.objects.count(), 1)
        evento = Historial.objects.first()
        self.assertEqual(evento.tipo_evento, EspacioService.DESACTIVACION)
        self.assertEqual(evento.object_id, espacio.pk)


# ---------------------------------------------------------------------------
# Integración — EspacioUsuarioService
# ---------------------------------------------------------------------------

class HistorialIntegracionEspacioUsuarioTests(TestCase):
    """Verifica que EspacioUsuarioService emite los eventos correctos al historial."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin@example.com',
            username='admin',
            nombre='Ada',
            rol='admin',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            rol='docente',
        )
        self.espacio = Espacio.objects.create(
            codigo_espacio='LAB-202',
            tipo='laboratorio',
            pabellon='Pabellón 2',
            piso='2',
        )
        self.service = EspacioUsuarioService()

    def test_asignar_usuario_registra_evento(self):
        """Asignar un usuario a un espacio genera un evento en el historial."""
        self.service.create(
            {
                'usuario_id': self.docente.id,
                'espacio_id': self.espacio.id,
                'tipo_responsabilidad': 'docente',
            },
            actor=self.admin,
        )

        self.assertEqual(Historial.objects.count(), 1)
        evento = Historial.objects.first()
        self.assertEqual(evento.tipo_evento, EspacioUsuarioService.ASIGNACION_USUARIO)
        self.assertEqual(evento.datos_extra['usuario_id'], self.docente.id)
        self.assertEqual(evento.datos_extra['espacio_id'], self.espacio.id)

    def test_retirar_usuario_registra_evento(self):
        """Retirar un usuario de un espacio genera un evento en el historial."""
        asignacion = self.service.create(
            {'usuario_id': self.docente.id, 'espacio_id': self.espacio.id},
            actor=self.admin,
        )
        Historial.objects.all().delete()

        self.service.delete(asignacion.id, actor=self.admin)

        self.assertEqual(Historial.objects.count(), 1)
        evento = Historial.objects.first()
        self.assertEqual(evento.tipo_evento, EspacioUsuarioService.RETIRO_USUARIO)
