from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from rest_framework.test import APITestCase
from django.urls import reverse

from espacios.models import Ciudad, Edificio, Espacio, Local
from usuarios.models import Usuario, UsuarioSede


class LocalAPITests(APITestCase):
    """Comprueba el contrato, permisos y reglas de locales y edificios."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin-locales@example.com',
            username='admin_locales',
            nombre='Ada',
            rol='admin',
        )
        self.tecnico = Usuario.objects.create_user(
            correo='tecnico-locales@example.com',
            username='tecnico_locales',
            nombre='Tomás',
            rol='tecnico',
        )
        self.usuario = Usuario.objects.create_user(
            correo='usuario-locales@example.com',
            username='usuario_locales',
            nombre='Úrsula',
            rol='usuario',
        )
        self.url = reverse('local-list')
        self.ciudad = self.crear_ciudad('Lima')
        self.payload = {
            'codigo': ' loc-01 ',
            'nombre': 'Campus Norte',
            'ciudad_id': self.ciudad.id,
            'tipo': 'campus',
            'descripcion': 'Sede principal',
            'activo': True,
        }

    @staticmethod
    def crear_ciudad(nombre):
        clave = Ciudad.normalizar_nombre(nombre)
        return Ciudad.objects.get_or_create(
            nombre_normalizado=clave,
            defaults={'nombre': nombre},
        )[0]

    def test_admin_creates_normalized_local_and_paginates(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.url, self.payload, format='json')
        listed = self.client.get(self.url, {'search': 'Lima'})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['codigo'], 'LOC-01')
        self.assertEqual(response.data['ciudad'], 'Lima')
        self.assertEqual(response.data['ciudad_id'], self.ciudad.id)
        self.assertEqual(response.data['tipo'], 'campus')
        self.assertEqual(listed.data['count'], 1)

    def test_local_creation_requires_a_city_from_the_catalog(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.url,
            {**self.payload, 'ciudad': 'Lima', 'ciudad_id': None},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('ciudad_id', response.data['errores'])

    def test_tecnico_reads_but_cannot_write_and_regular_user_is_blocked(self):
        Local.objects.create(codigo='LOC-01', nombre='Norte', ciudad=self.ciudad)
        self.client.force_authenticate(self.tecnico)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 403)

        self.client.force_authenticate(self.usuario)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_superadmin_lists_all_active_locations(self):
        """Garantiza que el catálogo de sedes del formulario no se limite por sede."""
        superadmin = Usuario.objects.create_superuser(
            correo='superadmin-locales@example.com',
            username='superadmin_locales',
            nombre='Leonardo',
            password='SuperAdminPass123',
        )
        first = Local.objects.create(codigo='LOC-01', nombre='Norte', ciudad=self.ciudad)
        second = Local.objects.create(
            codigo='LOC-02', nombre='Sur', ciudad=self.crear_ciudad('Cusco')
        )
        Local.objects.create(
            codigo='LOC-03',
            nombre='Inactiva',
            ciudad=self.crear_ciudad('Piura'),
            activo=False,
        )
        self.client.force_authenticate(superadmin)

        response = self.client.get(
            self.url,
            {'activo': 'true', 'asignables': 'true', 'page_size': 100},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            {item['id'] for item in response.data['results']},
            {first.id, second.id},
        )

    def test_assignable_locations_are_scoped_for_admin_and_responsable(self):
        """Limita el selector a las sedes vinculadas al actor territorial."""
        first = Local.objects.create(codigo='LOC-01', nombre='Norte', ciudad=self.ciudad)
        second = Local.objects.create(
            codigo='LOC-02', nombre='Sur', ciudad=self.crear_ciudad('Cusco')
        )
        responsable = Usuario.objects.create_user(
            correo='responsable-locales@example.com',
            username='responsable_locales',
            nombre='Rosa',
            rol='responsable',
        )
        UsuarioSede.objects.create(usuario=self.admin, local=first, activo=True)
        UsuarioSede.objects.create(usuario=responsable, local=second, activo=True)

        for actor, expected_id in ((self.admin, first.id), (responsable, second.id)):
            with self.subTest(rol=actor.rol):
                self.client.force_authenticate(actor)
                response = self.client.get(
                    self.url,
                    {'activo': 'true', 'asignables': 'true', 'page_size': 100},
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['count'], 1)
                self.assertEqual(response.data['results'][0]['id'], expected_id)

    def test_edificio_assigns_reassigns_and_filters_by_local(self):
        first = Local.objects.create(codigo='LOC-01', nombre='Norte', ciudad=self.ciudad)
        second = Local.objects.create(
            codigo='LOC-02', nombre='Sur', ciudad=self.crear_ciudad('Cusco')
        )
        self.client.force_authenticate(self.admin)
        created = self.client.post(
            reverse('edificio-list'),
            {'codigo': 'EDIF-01', 'nombre': 'Bloque A', 'local_id': first.id},
            format='json',
        )
        edificio_id = created.data['id']
        edificio = Edificio.objects.get(id=edificio_id)
        espacio = Espacio.objects.create(
            codigo_espacio='LAB-LOCAL-01',
            tipo='laboratorio',
            pabellon='Bloque A',
            edificio=edificio,
            piso='1',
            configuracion_plano={'filas': 3, 'columnas': 4, 'puestos': []},
        )
        edificio.configuracion_croquis = {
            'version': 1,
            'pisos': {'1': {'filas': 3, 'columnas': 4, 'ambientes': [], 'pasillos': []}},
        }
        edificio.save(update_fields=['configuracion_croquis'])
        croquis_before = edificio.configuracion_croquis
        plano_before = espacio.configuracion_plano

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['local_id'], first.id)
        self.assertEqual(created.data['local']['ciudad'], 'Lima')

        moved = self.client.patch(
            reverse('edificio-detail', args=[edificio_id]),
            {'local_id': second.id},
            format='json',
        )
        filtered = self.client.get(reverse('edificio-list'), {'local_id': second.id})

        self.assertEqual(moved.status_code, 200)
        self.assertEqual(moved.data['local']['codigo'], 'LOC-02')
        self.assertEqual(filtered.data['count'], 1)
        edificio.refresh_from_db()
        espacio.refresh_from_db()
        self.assertEqual(edificio.configuracion_croquis, croquis_before)
        self.assertEqual(espacio.configuracion_plano, plano_before)
        self.assertEqual(espacio.edificio_id, edificio_id)

    def test_building_assignment_rejects_inactive_or_deleted_local(self):
        local = Local.objects.create(
            codigo='LOC-01', nombre='Norte', ciudad=self.ciudad, activo=False
        )
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse('edificio-list'),
            {'codigo': 'EDIF-01', 'nombre': 'Bloque A', 'local_id': local.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('local_id', response.data['errores'])

    def test_building_filter_rejects_invalid_local_id(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse('edificio-list'), {'local_id': 'invalid'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('local_id', response.data['errores'])

    def test_local_deactivation_is_blocked_by_any_non_deleted_building(self):
        local = Local.objects.create(codigo='LOC-01', nombre='Norte', ciudad=self.ciudad)
        Edificio.objects.create(codigo='EDIF-01', nombre='Bloque A', local=local, activo=False)
        self.client.force_authenticate(self.admin)

        patch_response = self.client.patch(
            reverse('local-detail', args=[local.id]),
            {'activo': False},
            format='json',
        )
        delete_response = self.client.delete(reverse('local-detail', args=[local.id]))

        self.assertEqual(patch_response.status_code, 400)
        self.assertEqual(delete_response.status_code, 400)
        local.refresh_from_db()
        self.assertTrue(local.activo)
        self.assertFalse(local.is_deleted)

    def test_local_can_be_deleted_when_it_has_no_buildings(self):
        local = Local.objects.create(codigo='LOC-01', nombre='Norte', ciudad=self.ciudad)
        self.client.force_authenticate(self.admin)

        response = self.client.delete(reverse('local-detail', args=[local.id]))

        self.assertEqual(response.status_code, 204)
        local.refresh_from_db()
        self.assertFalse(local.activo)
        self.assertTrue(local.is_deleted)

    def test_legacy_building_keeps_null_local_and_croquis_spaces(self):
        edificio = Edificio.objects.create(
            codigo='EDIF-01',
            nombre='Bloque A',
            configuracion_croquis={'version': 1, 'pisos': {'1': {'ambientes': []}}},
        )
        espacio = Espacio.objects.create(
            codigo_espacio='LAB-101',
            tipo='laboratorio',
            pabellon='Bloque A',
            edificio=edificio,
            piso='1',
            configuracion_plano={'filas': 2, 'columnas': 2},
        )

        edificio.refresh_from_db()
        espacio.refresh_from_db()
        self.assertIsNone(edificio.local_id)
        self.assertEqual(edificio.configuracion_croquis['version'], 1)
        self.assertEqual(espacio.configuracion_plano['filas'], 2)


class CiudadAPITests(APITestCase):
    """Comprueba que el catálogo evita duplicados por acentos o mayúsculas."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin-ciudades@example.com',
            username='admin_ciudades',
            nombre='Ada',
            rol='admin',
        )
        self.url = reverse('ciudad-list')

    def test_admin_creates_and_lists_city_catalog_entries(self):
        self.client.force_authenticate(self.admin)

        created = self.client.post(self.url, {'nombre': '  Huánuco  '}, format='json')
        listed = self.client.get(self.url, {'search': 'Huánuco'})

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['nombre'], 'Huánuco')
        self.assertEqual(listed.data['count'], 1)
        self.assertEqual(listed.data['results'][0]['id'], created.data['id'])

    def test_city_name_is_unique_ignoring_accents_case_and_extra_spaces(self):
        self.client.force_authenticate(self.admin)

        first = self.client.post(self.url, {'nombre': 'Huánuco'}, format='json')
        duplicate = self.client.post(self.url, {'nombre': '  HUANUCO  '}, format='json')

        self.assertEqual(first.status_code, 201)
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn('nombre', duplicate.data['errores'])
        self.assertEqual(Ciudad.objects.filter(is_deleted=False).count(), 1)


class LocalSchemaMigrationTests(TransactionTestCase):
    """Comprueba que la migración deja la información histórica intacta."""

    migrate_from = [('espacios', '0007_edificio_configuracion_croquis')]
    migrate_to = [('espacios', '0008_local_edificio_local')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        EdificioHistorico = old_apps.get_model('espacios', 'Edificio')
        EspacioHistorico = old_apps.get_model('espacios', 'Espacio')
        EdificioHistorico.objects.create(
            codigo='EDIF-HIST-01',
            nombre='Edificio histórico',
            configuracion_croquis={'version': 1, 'pisos': {}},
        )
        EspacioHistorico.objects.create(
            codigo_espacio='LAB-HIST-01',
            tipo='laboratorio',
            pabellon='Edificio histórico',
            piso='1',
            configuracion_plano={'filas': 2, 'columnas': 2},
        )
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        self.apps = executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_additive_migration_keeps_legacy_relations_and_empty_local_catalog(self):
        LocalMigrado = self.apps.get_model('espacios', 'Local')
        EdificioMigrado = self.apps.get_model('espacios', 'Edificio')
        EspacioMigrado = self.apps.get_model('espacios', 'Espacio')

        self.assertEqual(LocalMigrado.objects.count(), 0)
        edificio = EdificioMigrado.objects.get(codigo='EDIF-HIST-01')
        espacio = EspacioMigrado.objects.get(codigo_espacio='LAB-HIST-01')
        self.assertIsNone(edificio.local_id)
        self.assertEqual(edificio.configuracion_croquis['version'], 1)
        self.assertEqual(espacio.configuracion_plano['filas'], 2)


class CiudadDataMigrationTests(TransactionTestCase):
    """Verifica que las ciudades textuales existentes se normalicen al migrar."""

    migrate_from = [('espacios', '0012_allow_duplicate_space_codes')]
    migrate_to = [('espacios', '0013_ciudad_catalogo')]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        LocalHistorico = old_apps.get_model('espacios', 'Local')
        LocalHistorico.objects.create(
            codigo='LOC-MIG-HCO-1', nombre='Campus 1', ciudad='Huánuco'
        )
        LocalHistorico.objects.create(
            codigo='LOC-MIG-HCO-2', nombre='Campus 2', ciudad=' HUANUCO '
        )
        LocalHistorico.objects.create(
            codigo='LOC-MIG-LIMA', nombre='Campus Lima', ciudad='Lima'
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        self.apps = executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_legacy_city_values_share_normalized_catalog_records(self):
        CiudadMigrada = self.apps.get_model('espacios', 'Ciudad')
        LocalMigrado = self.apps.get_model('espacios', 'Local')
        sedes_huanuco = LocalMigrado.objects.filter(codigo__contains='HCO')

        self.assertEqual(CiudadMigrada.objects.count(), 2)
        self.assertEqual(sedes_huanuco.values_list('ciudad_id', flat=True).distinct().count(), 1)
        self.assertEqual(
            CiudadMigrada.objects.get(nombre_normalizado='huanuco').nombre,
            'Huánuco',
        )
