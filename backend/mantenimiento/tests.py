from datetime import date

from django.test import TestCase

from equipos.models import Equipo
from espacios.models import Espacio
from mantenimiento.services import MantenimientoService
from usuarios.models import Usuario


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
