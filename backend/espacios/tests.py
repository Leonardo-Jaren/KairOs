from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from equipos.models import Equipo
from espacios.models import Espacio, EspacioUsuario
from espacios.repositories import EspacioRepository, EspacioUsuarioRepository
from espacios.services import EspacioService, EspacioUsuarioService
from usuarios.models import Usuario


class EspacioRepositoryServiceTests(TestCase):
    """Verifica persistencia y reglas del módulo de espacios."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin.spaces@example.com',
            username='adminspaces',
            nombre='Ada',
            rol='admin',
        )
        self.repository = EspacioRepository()
        self.service = EspacioService()

    def test_create_normalizes_code_and_records_audit(self):
        espacio = self.service.create(
            {
                'codigo_espacio': ' lab-301 ',
                'tipo': 'laboratorio',
                'pabellon': 'Pabellón 3',
                'piso': '3',
                'activo': True,
            },
            actor=self.admin,
        )

        self.assertEqual(espacio.codigo_espacio, 'LAB-301')
        self.assertEqual(espacio.created_by, self.admin)
        self.assertTrue(espacio.activo)

    def test_rejects_duplicate_code_case_insensitive(self):
        payload = {
            'codigo_espacio': 'LAB-301',
            'tipo': 'laboratorio',
            'pabellon': 'Pabellón 3',
            'piso': '3',
        }
        self.service.create(payload, actor=self.admin)

        with self.assertRaisesMessage(Exception, 'Ya existe un espacio'):
            self.service.create(
                {**payload, 'codigo_espacio': 'lab-301'},
                actor=self.admin,
            )

    def test_statistics_include_assigned_equipment(self):
        espacio = self.service.create(
            {
                'codigo_espacio': 'LAB-302',
                'tipo': 'laboratorio',
                'pabellon': 'Pabellón 3',
                'piso': '3',
            },
            actor=self.admin,
        )
        Equipo.objects.create(
            espacio=espacio,
            codigo='PC-001',
            numero_serie='SERIE-001',
            tipo_equipo='desktop',
            marca='Lenovo',
            modelo='ThinkCentre',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 1),
        )

        stats = self.service.get_estadisticas()

        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['laboratorios'], 1)
        self.assertEqual(stats['equipos'], 1)

    def test_delete_is_logical_and_hides_space(self):
        espacio = self.service.create(
            {
                'codigo_espacio': 'OF-201',
                'tipo': 'oficina',
                'pabellon': 'Pabellón 2',
                'piso': '2',
            },
            actor=self.admin,
        )

        self.service.delete(espacio.id, actor=self.admin)
        espacio.refresh_from_db()

        self.assertTrue(espacio.is_deleted)
        self.assertFalse(espacio.activo)
        self.assertIsNone(self.repository.get_by_id(espacio.id))


class EspacioAPITests(APITestCase):
    """Comprueba permisos y contrato HTTP del CRUD de espacios."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin.api@example.com',
            username='adminapi',
            nombre='Ada',
            rol='admin',
        )
        self.tecnico = Usuario.objects.create_user(
            correo='tecnico.api@example.com',
            username='tecnicoapi',
            nombre='Tomás',
            rol='tecnico',
        )
        self.usuario = Usuario.objects.create_user(
            correo='usuario.api@example.com',
            username='usuarioapi',
            nombre='Luis',
            rol='usuario',
        )
        self.list_url = reverse('espacio-list')
        self.payload = {
            'codigo_espacio': 'LAB-401',
            'tipo': 'laboratorio',
            'pabellon': 'Pabellón 4',
            'piso': '4',
            'activo': True,
        }

    def test_admin_creates_lists_and_retrieves_space(self):
        self.client.force_authenticate(self.admin)

        created = self.client.post(self.list_url, self.payload, format='json')
        listed = self.client.get(self.list_url, {'search': 'LAB-401'})
        detail = self.client.get(
            reverse('espacio-detail', args=[created.data['id']])
        )

        self.assertEqual(created.status_code, 201)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data['count'], 1)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['equipos'], [])

    def test_statistics_endpoint_returns_module_totals(self):
        self.client.force_authenticate(self.admin)
        self.client.post(self.list_url, self.payload, format='json')

        response = self.client.get(reverse('espacio-estadisticas'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['activos'], 1)

    def test_admin_saves_interactive_layout(self):
        espacio = Espacio.objects.create(**self.payload)
        equipo = Equipo.objects.create(
            espacio=espacio,
            codigo='PC-PLANO-01',
            numero_serie='SERIE-PLANO-01',
            tipo_equipo='desktop',
            marca='Lenovo',
            modelo='ThinkCentre',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 1),
        )
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse('espacio-disposicion', args=[espacio.id]),
            {
                'columnas': 4,
                'filas': 3,
                'puestos': [{
                    'equipo_id': equipo.id,
                    'fila': 1,
                    'columna': 2,
                    'es_docente': True,
                }],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        espacio.refresh_from_db()
        self.assertEqual(espacio.configuracion_plano['columnas'], 4)
        self.assertEqual(
            espacio.configuracion_plano['puestos'][0]['equipo_id'],
            equipo.id,
        )
        self.assertTrue(response.data['configuracion_plano']['puestos'][0]['es_docente'])

    def test_layout_rejects_equipment_from_another_space(self):
        espacio = Espacio.objects.create(**self.payload)
        otro_espacio = Espacio.objects.create(
            **{**self.payload, 'codigo_espacio': 'LAB-OTRO'}
        )
        equipo_ajeno = Equipo.objects.create(
            espacio=otro_espacio,
            codigo='PC-AJENA-01',
            numero_serie='SERIE-AJENA-01',
            tipo_equipo='desktop',
            marca='HP',
            modelo='ProDesk',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 1),
        )
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse('espacio-disposicion', args=[espacio.id]),
            {
                'columnas': 4,
                'filas': 2,
                'puestos': [{
                    'equipo_id': equipo_ajeno.id,
                    'fila': 1,
                    'columna': 1,
                    'es_docente': False,
                }],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        espacio.refresh_from_db()
        self.assertEqual(espacio.configuracion_plano, {})

    def test_layout_rejects_multiple_teacher_stations(self):
        espacio = Espacio.objects.create(**self.payload)
        equipos = [
            Equipo.objects.create(
                espacio=espacio,
                codigo=f'PC-DOCENTE-{index}',
                numero_serie=f'SERIE-DOCENTE-{index}',
                tipo_equipo='desktop',
                marca='HP',
                modelo='ProDesk',
                modo_adquisicion='comprado',
                fecha_adquisicion=date(2026, 1, 1),
            )
            for index in range(1, 3)
        ]
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse('espacio-disposicion', args=[espacio.id]),
            {
                'columnas': 4,
                'filas': 2,
                'puestos': [
                    {
                        'equipo_id': equipo.id,
                        'fila': 1,
                        'columna': index,
                        'es_docente': True,
                    }
                    for index, equipo in enumerate(equipos, start=1)
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_tecnico_has_read_only_access(self):
        Espacio.objects.create(**self.payload)
        self.client.force_authenticate(self.tecnico)

        read_response = self.client.get(self.list_url)
        write_response = self.client.post(
            self.list_url,
            {**self.payload, 'codigo_espacio': 'LAB-402'},
            format='json',
        )

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(write_response.status_code, 403)

    def test_regular_user_cannot_access_spaces(self):
        self.client.force_authenticate(self.usuario)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)


class EspacioUsuarioRepositoryServiceTests(TestCase):
    """Verifica persistencia y reglas de asignaciones usuario–espacio."""

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
        self.repository = EspacioUsuarioRepository()
        self.service = EspacioUsuarioService()

    def test_create_assignment_records_audit_fields(self):
        """Registra usuario, espacio, responsabilidad y autor."""
        assignment = self.service.create(
            {
                'usuario_id': self.docente.id,
                'espacio_id': self.espacio.id,
                'tipo_responsabilidad': 'docente',
            },
            actor=self.admin,
        )

        self.assertEqual(assignment.usuario, self.docente)
        self.assertEqual(assignment.espacio, self.espacio)
        self.assertEqual(assignment.created_by, self.admin)
        self.assertTrue(assignment.activo)

    def test_rejects_duplicate_assignment(self):
        """Impide repetir el mismo par usuario–espacio."""
        payload = {
            'usuario_id': self.docente.id,
            'espacio_id': self.espacio.id,
        }
        self.service.create(payload, actor=self.admin)

        with self.assertRaisesMessage(Exception, 'ya está asignado'):
            self.service.create(payload, actor=self.admin)

    def test_rejects_missing_relations(self):
        """Reporta identificadores que no corresponden a registros vigentes."""
        with self.assertRaisesMessage(Exception, 'El usuario no existe'):
            self.service.create(
                {'usuario_id': 999, 'espacio_id': self.espacio.id},
                actor=self.admin,
            )

    def test_soft_delete_hides_assignment(self):
        """Conserva físicamente la asignación y la excluye de consultas."""
        assignment = self.service.create(
            {
                'usuario_id': self.docente.id,
                'espacio_id': self.espacio.id,
            },
            actor=self.admin,
        )

        self.service.delete(assignment.id, actor=self.admin)
        assignment.refresh_from_db()

        self.assertTrue(assignment.is_deleted)
        self.assertFalse(assignment.activo)
        self.assertEqual(self.repository.get_all().count(), 0)

    def test_create_restores_a_soft_deleted_assignment(self):
        """Permite volver a asignar un usuario retirado del espacio."""
        payload = {
            'usuario_id': self.docente.id,
            'espacio_id': self.espacio.id,
        }
        assignment = self.service.create(payload, actor=self.admin)
        self.service.delete(assignment.id, actor=self.admin)

        restored = self.service.create(
            {**payload, 'tipo_responsabilidad': 'docente'},
            actor=self.admin,
        )

        self.assertEqual(restored.id, assignment.id)
        self.assertFalse(restored.is_deleted)
        self.assertTrue(restored.activo)
        self.assertEqual(restored.tipo_responsabilidad, 'docente')


class EspacioUsuarioAPITests(APITestCase):
    """Comprueba seguridad y contrato HTTP de asignaciones."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin@example.com',
            username='admin',
            nombre='Ada',
            rol='admin',
        )
        self.tecnico = Usuario.objects.create_user(
            correo='tecnico@example.com',
            username='tecnico',
            nombre='Tomás',
            rol='tecnico',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente@example.com',
            username='docente',
            nombre='Diana',
            apellido='Docente',
            rol='docente',
        )
        self.espacio = Espacio.objects.create(
            codigo_espacio='LAB-202',
            tipo='laboratorio',
            pabellon='Pabellón 2',
            piso='2',
        )
        self.list_url = reverse('espacio-usuario-list')
        self.payload = {
            'usuario_id': self.docente.id,
            'espacio_id': self.espacio.id,
            'tipo_responsabilidad': 'docente',
            'activo': True,
        }

    def test_requires_authentication(self):
        """Rechaza consultas sin credenciales."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 401)

    def test_admin_creates_and_lists_assignment(self):
        """Crea y representa una asignación con relaciones expandidas."""
        self.client.force_authenticate(self.admin)

        created = self.client.post(self.list_url, self.payload, format='json')
        listed = self.client.get(self.list_url, {'search': 'LAB-202'})

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['usuario']['id'], self.docente.id)
        self.assertEqual(created.data['espacio']['id'], self.espacio.id)
        self.assertEqual(listed.data['count'], 1)

    def test_duplicate_returns_validation_error(self):
        """Responde 400 cuando la asignación ya existe."""
        self.client.force_authenticate(self.admin)
        self.client.post(self.list_url, self.payload, format='json')

        response = self.client.post(self.list_url, self.payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data['errores'])

    def test_tecnico_has_read_only_access(self):
        """Permite consultas a técnicos y bloquea modificaciones."""
        self.client.force_authenticate(self.tecnico)

        read_response = self.client.get(self.list_url)
        write_response = self.client.post(
            self.list_url,
            self.payload,
            format='json',
        )

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(write_response.status_code, 403)
        options_response = self.client.get(reverse('espacio-usuario-opciones'))
        self.assertEqual(options_response.status_code, 403)

    def test_options_expose_only_required_fields(self):
        """Entrega catálogos mínimos para construir el formulario."""
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse('espacio-usuario-opciones'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['espacios']), 1)
        self.assertEqual(response.data['espacios'][0]['codigo_espacio'], 'LAB-202')
        self.assertGreaterEqual(len(response.data['usuarios']), 3)

    def test_delete_is_logical(self):
        """Marca la asignación eliminada mediante el endpoint DELETE."""
        self.client.force_authenticate(self.admin)
        assignment = EspacioUsuario.objects.create(
            usuario=self.docente,
            espacio=self.espacio,
            created_by=self.admin,
            updated_by=self.admin,
        )

        response = self.client.delete(
            reverse('espacio-usuario-detail', args=[assignment.id])
        )
        assignment.refresh_from_db()

        self.assertEqual(response.status_code, 204)
        self.assertTrue(assignment.is_deleted)
