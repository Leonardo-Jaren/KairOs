from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APITestCase

from equipos.models import Equipo
from espacios.models import Espacio
from incidencias.models import Incidencia
from incidencias.services import IncidenciaService
from mantenimiento.models import Mantenimiento
from mantenimiento.services import MantenimientoService
from usuarios.models import Usuario


class FlujoIncidenciaMantenimientoTests(TestCase):
    """Verifica el ciclo integrado de reportes y órdenes de trabajo."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin.incidence@example.com',
            username='adminincidence',
            nombre='Ada',
            rol='admin',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente.incidence@example.com',
            username='docenteincidence',
            nombre='Grace',
            rol='docente',
        )
        self.espacio = Espacio.objects.create(
            codigo_espacio='LAB-INCI-01',
            tipo='laboratorio',
            pabellon='Edificio 1',
            piso='1',
        )
        self.otro_espacio = Espacio.objects.create(
            codigo_espacio='LAB-INCI-02',
            tipo='laboratorio',
            pabellon='Edificio 1',
            piso='2',
        )
        self.equipo = Equipo.objects.create(
            espacio=self.espacio,
            codigo='PC-INCI-01',
            numero_serie='SERIE-INCI-01',
            tipo_equipo='desktop',
            marca='Lenovo',
            modelo='ThinkCentre',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 1),
        )
        self.service = IncidenciaService()
        self.mantenimiento_service = MantenimientoService()

    def _incidencia_data(self, **overrides):
        data = {
            'espacio': self.espacio,
            'equipo': self.equipo,
            'tipo_incidencia': 'hardware',
            'prioridad': 'alta',
            'descripcion': 'La estación no enciende.',
        }
        data.update(overrides)
        return data

    def _create_incidence(self, actor=None, **overrides):
        return self.service.create(
            self._incidencia_data(**overrides),
            actor=actor or self.admin,
        )

    def test_new_report_is_always_pending_and_validates_equipment_space(self):
        incidence = self._create_incidence(estado='resuelto', resolucion='No debe aceptarse')

        self.assertEqual(incidence.estado, 'pendiente')
        self.assertIsNone(incidence.fecha_resolucion)

        with self.assertRaises(ValidationError):
            self._create_incidence(espacio=self.otro_espacio)

    def test_transition_requires_resolution_and_terminal_incidence_is_immutable(self):
        incidence = self._create_incidence()

        with self.assertRaises(ValidationError):
            self.service.update(incidence.id, {'estado': 'cerrado'}, actor=self.admin)

        with self.assertRaises(ValidationError):
            self.service.update(incidence.id, {'estado': 'resuelto'}, actor=self.admin)

        incidence = self.service.update(
            incidence.id,
            {'estado': 'en_proceso'},
            actor=self.admin,
        )
        incidence = self.service.update(
            incidence.id,
            {'estado': 'resuelto', 'resolucion': 'Se ajustó la fuente.'},
            actor=self.admin,
        )
        self.assertIsNotNone(incidence.fecha_resolucion)
        incidence = self.service.update(incidence.id, {'estado': 'cerrado'}, actor=self.admin)
        self.assertEqual(incidence.estado, 'cerrado')

        with self.assertRaises(ValidationError):
            self.service.update(incidence.id, {'descripcion': 'Cambio no permitido'}, actor=self.admin)

    def test_reporter_only_sees_and_cannot_update_own_scope(self):
        own = self._create_incidence(actor=self.docente)
        other = self._create_incidence(actor=self.admin, descripcion='Otro reporte')

        self.assertEqual(list(self.service.listar(actor=self.docente)), [own])
        with self.assertRaises(NotFound):
            self.service.get_visible_by_id(other.id, actor=self.docente)
        with self.assertRaises(NotFound):
            self.service.update(other.id, {'estado': 'en_proceso'}, actor=self.docente)

    def test_corrective_from_incidence_links_same_equipment_and_marks_incidence_in_process(self):
        incidence = self._create_incidence()

        maintenance = self.mantenimiento_service.create(
            {
                'equipo_id': self.equipo.id,
                'incidencia_id': incidence.id,
                'fecha': date(2026, 9, 24),
                'tipo_mantenimiento': 'correctivo',
                'estado': 'en_proceso',
                'descripcion': 'Diagnóstico y reparación.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )

        incidence.refresh_from_db()
        self.assertEqual(maintenance.incidencia_origen_id, incidence.id)
        self.assertEqual(incidence.estado, 'en_proceso')
        self.assertEqual(maintenance.equipo_id, incidence.equipo_id)

        with self.assertRaises(ValidationError):
            self.mantenimiento_service.create(
                {
                    'equipo_id': self.equipo.id,
                    'incidencia_id': incidence.id,
                    'fecha': date(2026, 9, 24),
                    'tipo_mantenimiento': 'preventivo',
                    'estado': 'pendiente',
                    'descripcion': 'No debe enlazarse.',
                    'tecnicos_ids': [],
                },
                actor=self.admin,
            )

    def test_functional_corrective_finishes_and_closes_incidence_atomically(self):
        incidence = self._create_incidence()
        maintenance = self.mantenimiento_service.create(
            {
                'equipo_id': self.equipo.id,
                'incidencia_id': incidence.id,
                'fecha': date(2026, 9, 24),
                'tipo_mantenimiento': 'correctivo',
                'estado': 'en_proceso',
                'descripcion': 'Diagnóstico y reparación.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )

        result = self.mantenimiento_service.finalizar(
            maintenance.id,
            {
                'diagnostico': 'Fuente de poder defectuosa.',
                'trabajo_realizado': 'Se reemplazó la fuente y se probó el arranque.',
                'prueba_realizada': True,
                'observacion_prueba': 'El equipo inició correctamente.',
                'resultado_equipo': 'en_uso',
            },
            actor=self.admin,
        )

        incidence.refresh_from_db()
        maintenance.refresh_from_db()
        self.equipo.refresh_from_db()
        self.assertEqual(maintenance.estado, 'resuelto')
        self.assertTrue(maintenance.prueba_realizada)
        self.assertEqual(maintenance.verificado_por, self.admin)
        self.assertIsNotNone(maintenance.fecha_verificacion)
        self.assertEqual(incidence.estado, 'cerrado')
        self.assertEqual(incidence.resolucion, maintenance.trabajo_realizado)
        self.assertEqual(self.equipo.estado, 'en_uso')
        self.assertTrue(result['cerrada_automaticamente'])
        self.assertIsNone(result['siguiente_accion'])

    def test_damaged_corrective_finishes_but_keeps_incidence_open(self):
        incidence = self._create_incidence()
        maintenance = self.mantenimiento_service.create(
            {
                'equipo_id': self.equipo.id,
                'incidencia_id': incidence.id,
                'fecha': date(2026, 9, 24),
                'tipo_mantenimiento': 'correctivo',
                'estado': 'en_proceso',
                'descripcion': 'Diagnóstico y reparación.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )

        result = self.mantenimiento_service.finalizar(
            maintenance.id,
            {
                'diagnostico': 'La placa presenta daño irreversible.',
                'trabajo_realizado': 'Se realizaron pruebas de diagnóstico.',
                'prueba_realizada': True,
                'observacion_prueba': 'No supera la prueba de arranque.',
                'resultado_equipo': 'dañado',
            },
            actor=self.admin,
        )

        incidence.refresh_from_db()
        self.equipo.refresh_from_db()
        self.assertEqual(maintenance.__class__.objects.get(id=maintenance.id).estado, 'resuelto')
        self.assertEqual(incidence.estado, 'en_proceso')
        self.assertEqual(self.equipo.estado, 'dañado')
        self.assertFalse(result['cerrada_automaticamente'])
        self.assertEqual(result['siguiente_accion'], 'crear_correctivo')

    def test_damaged_corrective_reopens_a_resolved_incidence(self):
        incidence = self._create_incidence()
        self.service.update(incidence.id, {'estado': 'en_proceso'}, actor=self.admin)
        self.service.update(
            incidence.id,
            {'estado': 'resuelto', 'resolucion': 'Se aplicó un ajuste temporal.'},
            actor=self.admin,
        )
        maintenance = self.mantenimiento_service.create(
            {
                'equipo_id': self.equipo.id,
                'incidencia_id': incidence.id,
                'fecha': date(2026, 9, 24),
                'tipo_mantenimiento': 'correctivo',
                'estado': 'en_proceso',
                'descripcion': 'Nueva intervención correctiva.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )

        self.mantenimiento_service.finalizar(
            maintenance.id,
            {
                'diagnostico': 'La falla persiste.',
                'trabajo_realizado': 'Se realizaron nuevas pruebas.',
                'prueba_realizada': True,
                'resultado_equipo': 'dañado',
            },
            actor=self.admin,
        )

        incidence.refresh_from_db()
        self.assertEqual(incidence.estado, 'en_proceso')
        self.assertIsNone(incidence.fecha_resolucion)

    def test_resolving_maintenance_requires_work_and_updates_equipment_result(self):
        maintenance = self.mantenimiento_service.create(
            {
                'equipo_id': self.equipo.id,
                'fecha': date(2026, 9, 24),
                'tipo_mantenimiento': 'preventivo',
                'estado': 'en_proceso',
                'descripcion': 'Limpieza trimestral.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )

        with self.assertRaises(ValidationError):
            self.mantenimiento_service.update(
                maintenance.id,
                {'estado': 'resuelto'},
                actor=self.admin,
            )

        self.mantenimiento_service.update(
            maintenance.id,
            {
                'estado': 'resuelto',
                'diagnostico': 'Equipo limpio y operativo.',
                'trabajo_realizado': 'Limpieza interna y revisión.',
                'prueba_realizada': True,
                'resultado_equipo': 'en_uso',
            },
            actor=self.admin,
        )
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.estado, 'en_uso')
        self.assertEqual(Mantenimiento.objects.get(id=maintenance.id).resultado_equipo, 'en_uso')

    def test_removing_active_order_restores_equipment_when_no_other_order_exists(self):
        maintenance = self.mantenimiento_service.create(
            {
                'equipo_id': self.equipo.id,
                'fecha': date(2026, 9, 24),
                'tipo_mantenimiento': 'correctivo',
                'estado': 'en_proceso',
                'descripcion': 'Orden que se cancela administrativamente.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )
        self.mantenimiento_service.delete(maintenance.id, actor=self.admin)
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.estado, 'en_uso')


class IncidenciaAPIPermissionTests(APITestCase):
    """Comprueba que el rol reportante no pueda operar por HTTP."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin.api.incidence@example.com',
            username='adminapiincidence',
            nombre='Admin',
            rol='admin',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente.api.incidence@example.com',
            username='docenteapiincidence',
            nombre='Docente',
            rol='docente',
        )
        self.espacio = Espacio.objects.create(
            codigo_espacio='LAB-API-INCI',
            tipo='laboratorio',
            pabellon='Edificio API',
            piso='1',
        )
        self.equipo = Equipo.objects.create(
            espacio=self.espacio,
            codigo='PC-API-INCI',
            numero_serie='SERIE-API-INCI',
            tipo_equipo='desktop',
            marca='Dell',
            modelo='OptiPlex',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 1),
        )
        self.service = IncidenciaService()
        self.incidence = self.service.create(
            {
                'espacio': self.espacio,
                'equipo': self.equipo,
                'tipo_incidencia': 'hardware',
                'descripcion': 'Reporte propio.',
            },
            actor=self.docente,
        )
        self.other = self.service.create(
            {
                'espacio': self.espacio,
                'equipo': self.equipo,
                'tipo_incidencia': 'hardware',
                'descripcion': 'Reporte administrativo.',
            },
            actor=self.admin,
        )

    def test_docente_only_sees_own_incidents_and_cannot_patch(self):
        self.client.force_authenticate(self.docente)

        response = self.client.get(reverse('incidencia-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.incidence.id)

        response = self.client.patch(
            reverse('incidencia-detail', args=[self.incidence.id]),
            {'estado': 'en_proceso'},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_docente_cannot_retrieve_another_report(self):
        self.client.force_authenticate(self.docente)

        response = self.client.get(reverse('incidencia-detail', args=[self.other.id]))
        self.assertEqual(response.status_code, 404)


class MantenimientoActionAPITests(APITestCase):
    """Verifica las acciones guiadas de inicio y finalización."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin.api.mantenimiento@example.com',
            username='adminapimantenimiento',
            nombre='Ada',
            rol='admin',
        )
        self.espacio = Espacio.objects.create(
            codigo_espacio='LAB-API-MANT',
            tipo='laboratorio',
            pabellon='Edificio API',
            piso='1',
        )
        self.equipo = Equipo.objects.create(
            espacio=self.espacio,
            codigo='PC-API-MANT',
            numero_serie='SERIE-API-MANT',
            tipo_equipo='desktop',
            marca='Dell',
            modelo='OptiPlex',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 1),
        )
        self.mantenimiento_service = MantenimientoService()
        self.incidencia_service = IncidenciaService()
        self.client.force_authenticate(self.admin)

    def _create_ticket(self, **overrides):
        data = {
            'equipo_id': self.equipo.id,
            'fecha': date(2026, 9, 24),
            'tipo_mantenimiento': 'preventivo',
            'estado': 'pendiente',
            'descripcion': 'Revisión de rutina.',
            'tecnicos_ids': [],
        }
        data.update(overrides)
        return self.mantenimiento_service.create(data, actor=self.admin)

    def test_iniciar_action_moves_pending_ticket_to_attention(self):
        ticket = self._create_ticket()

        response = self.client.post(
            f'/api/v1/mantenimiento/{ticket.id}/iniciar/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['estado'], 'en_proceso')

    def test_finalize_action_closes_functional_corrective_and_returns_context(self):
        incidencia = self.incidencia_service.create(
            {
                'espacio': self.espacio,
                'equipo': self.equipo,
                'tipo_incidencia': 'hardware',
                'descripcion': 'La estación no enciende.',
            },
            actor=self.admin,
        )
        ticket = self._create_ticket(
            tipo_mantenimiento='correctivo',
            estado='en_proceso',
            incidencia_id=incidencia.id,
            descripcion='Diagnóstico y reparación.',
        )

        response = self.client.post(
            f'/api/v1/mantenimiento/{ticket.id}/finalizar/',
            {
                'diagnostico': 'Fuente defectuosa.',
                'trabajo_realizado': 'Se reemplazó la fuente y se probó el arranque.',
                'prueba_realizada': True,
                'observacion_prueba': 'Arranque correcto.',
                'resultado_equipo': 'en_uso',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['mantenimiento']['estado'], 'resuelto')
        self.assertEqual(response.data['equipo']['estado'], 'en_uso')
        self.assertEqual(response.data['incidencia']['estado'], 'cerrado')
        self.assertTrue(response.data['incidencia']['cerrada_automaticamente'])
        self.assertIsNone(response.data['siguiente_accion'])

    def test_finalize_action_requires_function_test(self):
        ticket = self._create_ticket(estado='en_proceso')

        response = self.client.post(
            f'/api/v1/mantenimiento/{ticket.id}/finalizar/',
            {
                'diagnostico': 'Revisión completada.',
                'trabajo_realizado': 'Se ajustaron conexiones.',
                'prueba_realizada': False,
                'resultado_equipo': 'en_uso',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('prueba_realizada', response.data['errores'])
