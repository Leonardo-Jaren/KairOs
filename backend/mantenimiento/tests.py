from datetime import date

from django.test import TestCase

from equipos.models import Equipo
from espacios.models import Espacio
from mantenimiento.serializers import MantenimientoSerializer
from mantenimiento.services import MantenimientoService
from usuarios.models import PerfilTecnico, Usuario


class MantenimientoEstadoEquipoTests(TestCase):
    """Verifica la sincronización operativa entre tickets y equipos."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin.maintenance@example.com',
            username='adminmaintenance',
            nombre='Ada',
            rol='admin',
        )
        self.espacio = Espacio.objects.create(
            codigo_espacio='LAB-501',
            tipo='laboratorio',
            pabellon='Edificio 5',
            piso='1',
        )
        self.equipo = Equipo.objects.create(
            espacio=self.espacio,
            codigo='PC-MANT-01',
            numero_serie='SERIE-MANT-01',
            tipo_equipo='desktop',
            marca='Lenovo',
            modelo='ThinkCentre',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 1),
        )
        self.service = MantenimientoService()

    def _ticket_data(self, **overrides):
        data = {
            'equipo_id': self.equipo.id,
            'fecha': date(2026, 8, 14),
            'tipo_mantenimiento': 'correctivo',
            'estado': 'pendiente',
            'descripcion': 'Revisión solicitada.',
            'tecnicos_ids': [],
        }
        data.update(overrides)
        return data

    def test_ticket_uses_authenticated_actor_as_default_reporter(self):
        ticket = self.service.create(self._ticket_data(), actor=self.admin)

        self.assertEqual(ticket.reportado_por, self.admin)
        self.assertEqual(
            MantenimientoSerializer(ticket).data['reportado_por'],
            {
                'id': self.admin.id,
                'nombre_completo': 'Ada',
                'correo': 'admin.maintenance@example.com',
                'rol': 'admin',
            },
        )

    def test_ticket_accepts_an_explicit_active_reporter(self):
        reportante = Usuario.objects.create_user(
            correo='reportante.maintenance@example.com',
            username='reportantemaintenance',
            nombre='Grace',
            apellido='Hopper',
            rol='docente',
        )

        ticket = self.service.create(
            self._ticket_data(reportado_por_id=reportante.id),
            actor=self.admin,
        )

        self.assertEqual(ticket.reportado_por, reportante)
        self.assertEqual(ticket.created_by, self.admin)

    def test_ticket_reporter_can_be_changed_to_an_active_user(self):
        ticket = self.service.create(self._ticket_data(), actor=self.admin)
        reportante = Usuario.objects.create_user(
            correo='nuevo.reportante@example.com',
            username='nuevoreportante',
            nombre='Katherine',
            apellido='Johnson',
            rol='usuario',
        )

        updated = self.service.update(
            ticket.id,
            {'reportado_por_id': reportante.id},
            actor=self.admin,
        )

        self.assertEqual(updated.reportado_por, reportante)

    def test_available_technicians_include_linked_user_id(self):
        tecnico = Usuario.objects.create_user(
            correo='tecnico.maintenance@example.com',
            username='tecnicomantenimiento',
            nombre='Margaret',
            apellido='Hamilton',
            rol='tecnico',
        )
        perfil = PerfilTecnico.objects.create(usuario=tecnico, area='Soporte')

        opciones = self.service.get_tecnicos_disponibles()

        self.assertIn(
            {
                'id': perfil.id,
                'usuario_id': tecnico.id,
                'nombre_completo': 'Margaret Hamilton',
                'area': 'Soporte',
            },
            opciones,
        )

    def test_ticket_in_progress_sends_equipment_to_maintenance(self):
        self.service.create(
            {
                'equipo_id': self.equipo.id,
                'fecha': date(2026, 8, 14),
                'tipo_mantenimiento': 'correctivo',
                'estado': 'en_proceso',
                'descripcion': 'El monitor no muestra imagen.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )

        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.estado, 'en_mantenimiento')

    def test_pending_report_keeps_current_equipment_status(self):
        self.service.create(
            {
                'equipo_id': self.equipo.id,
                'fecha': date(2026, 8, 14),
                'tipo_mantenimiento': 'correctivo',
                'estado': 'pendiente',
                'descripcion': 'El teclado presenta una tecla floja.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )

        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.estado, 'en_uso')

    def test_starting_pending_ticket_updates_equipment_status(self):
        ticket = self.service.create(
            {
                'equipo_id': self.equipo.id,
                'fecha': date(2026, 8, 14),
                'tipo_mantenimiento': 'correctivo',
                'estado': 'pendiente',
                'descripcion': 'Revisión pendiente.',
                'tecnicos_ids': [],
            },
            actor=self.admin,
        )

        self.service.update(
            ticket.id,
            {'estado': 'en_proceso'},
            actor=self.admin,
        )

        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.estado, 'en_mantenimiento')
