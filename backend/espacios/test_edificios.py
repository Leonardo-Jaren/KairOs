from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from espacios.models import Edificio, Espacio
from usuarios.models import Usuario


class EdificioAPITests(APITestCase):
    """Comprueba el CRUD, los permisos y la integración con espacios."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin-edificios@example.com',
            username='admin_edificios',
            nombre='Ada',
            rol='admin',
        )
        self.tecnico = Usuario.objects.create_user(
            correo='tecnico-edificios@example.com',
            username='tecnico_edificios',
            nombre='Tomás',
            rol='tecnico',
        )
        self.usuario = Usuario.objects.create_user(
            correo='usuario-edificios@example.com',
            username='usuario_edificios',
            nombre='Úrsula',
            rol='usuario',
        )
        self.list_url = reverse('edificio-list')
        self.payload = {
            'codigo': 'edif-01',
            'nombre': 'Edificio 1',
            'descripcion': 'Facultad de Ingeniería',
            'activo': True,
        }

    def test_requires_authentication(self):
        """Rechaza consultas de edificios sin credenciales."""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 401)

    def test_admin_creates_and_lists_building(self):
        """Normaliza el código y devuelve contadores operativos."""
        self.client.force_authenticate(self.admin)

        created = self.client.post(self.list_url, self.payload, format='json')
        listed = self.client.get(self.list_url, {'search': 'Ingeniería'})

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['codigo'], 'EDIF-01')
        self.assertEqual(created.data['cantidad_espacios'], 0)
        self.assertEqual(listed.data['count'], 1)

    def test_duplicate_code_returns_validation_error(self):
        """Impide códigos repetidos aunque varíen mayúsculas y minúsculas."""
        Edificio.objects.create(codigo='EDIF-01', nombre='Existente')
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.list_url, self.payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_tecnico_has_read_only_access(self):
        """Permite lectura al técnico y reserva la escritura al administrador."""
        Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        self.client.force_authenticate(self.tecnico)

        read_response = self.client.get(self.list_url)
        write_response = self.client.post(self.list_url, self.payload, format='json')

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(write_response.status_code, 403)

    def test_regular_user_cannot_access_buildings(self):
        """Bloquea el módulo para roles sin alcance operativo."""
        self.client.force_authenticate(self.usuario)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_is_logical_and_preserves_spaces(self):
        """Retira el edificio y deja sus espacios disponibles por pabellón."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        espacio = Espacio.objects.create(
            codigo_espacio='LAB-101',
            tipo='laboratorio',
            pabellon='Edificio 1',
            edificio=edificio,
            piso='1',
        )
        self.client.force_authenticate(self.admin)

        response = self.client.delete(reverse('edificio-detail', args=[edificio.id]))
        edificio.refresh_from_db()
        espacio.refresh_from_db()

        self.assertEqual(response.status_code, 204)
        self.assertTrue(edificio.is_deleted)
        self.assertFalse(edificio.activo)
        self.assertIsNone(espacio.edificio_id)
        self.assertEqual(espacio.pabellon, 'Edificio 1')

    def test_renaming_building_updates_legacy_pavilion(self):
        """Mantiene consistente el campo pabellón para clientes anteriores."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        espacio = Espacio.objects.create(
            codigo_espacio='LAB-102',
            tipo='laboratorio',
            pabellon='Edificio 1',
            edificio=edificio,
            piso='1',
        )
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse('edificio-detail', args=[edificio.id]),
            {'nombre': 'Pabellón de Ingeniería'},
            format='json',
        )
        espacio.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(espacio.pabellon, 'Pabellón de Ingeniería')

    def test_building_statistics_include_space_types(self):
        """Resume edificios, laboratorios y aulas vinculados."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        for codigo, tipo in [('LAB-101', 'laboratorio'), ('AUL-102', 'aula')]:
            Espacio.objects.create(
                codigo_espacio=codigo,
                tipo=tipo,
                pabellon='Edificio 1',
                edificio=edificio,
                piso='1',
            )
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse('edificio-estadisticas'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['espacios'], 2)
        self.assertEqual(response.data['pisos'], 1)
        self.assertEqual(response.data['laboratorios'], 1)
        self.assertEqual(response.data['aulas'], 1)

    def test_admin_saves_floor_sketch_with_rooms_and_corridor(self):
        """Persiste un croquis por piso con todos sus ambientes activos."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        laboratorio = Espacio.objects.create(
            codigo_espacio='LAB-101',
            tipo='laboratorio',
            pabellon=edificio.nombre,
            edificio=edificio,
            piso='Piso 1',
        )
        aula = Espacio.objects.create(
            codigo_espacio='AUL-102',
            tipo='aula',
            pabellon=edificio.nombre,
            edificio=edificio,
            piso='Piso 1',
        )
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse('edificio-croquis-piso', args=[edificio.id]),
            {
                'piso': '1',
                'filas': 5,
                'columnas': 8,
                'ambientes': [
                    {'espacio_id': laboratorio.id, 'fila': 1, 'columna': 1, 'ancho': 3, 'alto': 2},
                    {'espacio_id': aula.id, 'fila': 4, 'columna': 1, 'ancho': 2, 'alto': 1},
                ],
                'pasillos': [
                    {'fila': 3, 'columna': column} for column in range(1, 9)
                ],
            },
            format='json',
        )
        edificio.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(edificio.configuracion_croquis['version'], 1)
        self.assertEqual(
            len(edificio.configuracion_croquis['pisos']['1']['ambientes']),
            2,
        )

    def test_floor_sketch_rejects_overlapping_rooms(self):
        """Impide guardar dos ambientes sobre las mismas celdas."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        espacios = [
            Espacio.objects.create(
                codigo_espacio=f'LAB-10{index}',
                tipo='laboratorio',
                pabellon=edificio.nombre,
                edificio=edificio,
                piso='1',
            )
            for index in range(1, 3)
        ]
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse('edificio-croquis-piso', args=[edificio.id]),
            {
                'piso': '1',
                'filas': 5,
                'columnas': 8,
                'ambientes': [
                    {'espacio_id': espacios[0].id, 'fila': 1, 'columna': 1, 'ancho': 3, 'alto': 2},
                    {'espacio_id': espacios[1].id, 'fila': 2, 'columna': 2, 'ancho': 2, 'alto': 2},
                ],
                'pasillos': [],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('ambientes', response.data['errores'])

    def test_floor_sketch_rejects_non_numeric_floor(self):
        """Exige un identificador numérico al guardar el croquis del piso."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse('edificio-croquis-piso', args=[edificio.id]),
            {
                'piso': 'Primero',
                'filas': 5,
                'columnas': 8,
                'ambientes': [],
                'pasillos': [],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('piso', response.data['errores'])

    def test_tecnico_cannot_edit_floor_sketch(self):
        """Mantiene la edición del croquis reservada al administrador."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        self.client.force_authenticate(self.tecnico)

        response = self.client.patch(
            reverse('edificio-croquis-piso', args=[edificio.id]),
            {
                'piso': '1',
                'filas': 5,
                'columnas': 8,
                'ambientes': [],
                'pasillos': [],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_space_accepts_building_and_derives_legacy_pavilion(self):
        """Crea un espacio nuevo con edificio y mantiene pabellón en la salida."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Edificio 1')
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            reverse('espacio-list'),
            {
                'codigo_espacio': 'LAB-201',
                'tipo': 'laboratorio',
                'edificio_id': edificio.id,
                'piso': '2',
                'activo': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['pabellon'], 'Edificio 1')
        self.assertEqual(response.data['edificio_id'], edificio.id)
        self.assertEqual(response.data['edificio']['codigo'], 'EDIF-01')

    def test_legacy_space_contract_remains_valid(self):
        """Acepta espacios que solo envían el pabellón histórico."""
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            reverse('espacio-list'),
            {
                'codigo_espacio': 'LAB-202',
                'tipo': 'laboratorio',
                'pabellon': 'Pabellón histórico',
                'piso': '2',
                'activo': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['pabellon'], 'Pabellón histórico')
        self.assertIsNone(response.data['edificio'])

    def test_spaces_can_be_filtered_by_building(self):
        """Filtra por identificador y busca por nombre del edificio."""
        edificio = Edificio.objects.create(codigo='EDIF-01', nombre='Ingeniería')
        Espacio.objects.create(
            codigo_espacio='LAB-301',
            tipo='laboratorio',
            pabellon='Ingeniería',
            edificio=edificio,
            piso='3',
        )
        Espacio.objects.create(
            codigo_espacio='LAB-OTRO',
            tipo='laboratorio',
            pabellon='Otro bloque',
            piso='1',
        )
        self.client.force_authenticate(self.admin)

        by_id = self.client.get(reverse('espacio-list'), {'edificio_id': edificio.id})
        by_search = self.client.get(reverse('espacio-list'), {'search': 'Ingeniería'})

        self.assertEqual(by_id.data['count'], 1)
        self.assertEqual(by_search.data['count'], 1)
        self.assertEqual(by_id.data['results'][0]['codigo_espacio'], 'LAB-301')


class EdificioDataMigrationTests(TransactionTestCase):
    """Verifica la agrupación automática de pabellones históricos."""

    migrate_from = [('espacios', '0005_espacio_configuracion_plano')]
    migrate_to = [('espacios', '0006_edificio_espacio_edificio')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        EspacioHistorico = old_apps.get_model('espacios', 'Espacio')
        EspacioHistorico.objects.create(
            codigo_espacio='LAB-101',
            tipo='laboratorio',
            pabellon='Pabellón 1',
            piso='1',
        )
        EspacioHistorico.objects.create(
            codigo_espacio='AUL-102',
            tipo='aula',
            pabellon='  pabellón   1 ',
            piso='1',
        )
        EspacioHistorico.objects.create(
            codigo_espacio='LAB-201',
            tipo='laboratorio',
            pabellon='Edificio A',
            piso='2',
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        self.apps = executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_groups_equivalent_pavilions_and_links_spaces(self):
        """Crea un edificio por nombre normalizado y conserva todos los espacios."""
        EdificioMigrado = self.apps.get_model('espacios', 'Edificio')
        EspacioMigrado = self.apps.get_model('espacios', 'Espacio')

        self.assertEqual(EdificioMigrado.objects.count(), 2)
        self.assertEqual(
            EspacioMigrado.objects.exclude(edificio_id=None).count(),
            3,
        )
        primeros = EspacioMigrado.objects.filter(
            codigo_espacio__in=['LAB-101', 'AUL-102']
        ).values_list('edificio_id', flat=True)
        self.assertEqual(len(set(primeros)), 1)
