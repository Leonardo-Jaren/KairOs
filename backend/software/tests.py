from datetime import date, timedelta

from django.urls import reverse
from rest_framework.test import APITestCase

from equipos.models import Equipo
from espacios.models import Espacio
from software.models import ProductoSoftware, SoftwareInstalado
from usuarios.models import Usuario


class SoftwareAPITests(APITestCase):
    """Comprueba seguridad, contrato y licenciamiento del software por equipo."""

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo='admin.software@example.com',
            username='adminsoftware',
            nombre='Ada',
            rol='admin',
        )
        self.tecnico = Usuario.objects.create_user(
            correo='tecnico.software@example.com',
            username='tecnicosoftware',
            nombre='Tomas',
            rol='tecnico',
        )
        self.docente = Usuario.objects.create_user(
            correo='docente.software@example.com',
            username='docentesoftware',
            nombre='Diana',
            rol='docente',
        )
        self.espacio = Espacio.objects.create(
            codigo_espacio='LAB-SW-01',
            tipo='laboratorio',
            pabellon='Edificio 1',
            piso='1',
        )
        self.equipo = self._crear_equipo('PC-SW-01')
        self.otro_equipo = self._crear_equipo('PC-SW-02')
        self.producto = ProductoSoftware.objects.create(
            software='Suite Ofimatica',
            version='2026',
            descripcion='Herramientas para oficina.',
            tipo_licencia='volumen',
            licencias_totales=1,
            fecha_expiracion=date.today() + timedelta(days=365),
            costo_anual_total='1500.00',
        )
        self.productos_url = reverse('producto-software-list')
        self.instalaciones_url = reverse('software-instalado-list')

    def _crear_equipo(self, codigo: str) -> Equipo:
        """Construye un equipo vigente con identificadores irrepetibles."""
        return Equipo.objects.create(
            espacio=self.espacio,
            codigo=codigo,
            numero_serie=f'SERIE-{codigo}',
            tipo_equipo='desktop',
            marca='Lenovo',
            modelo='ThinkCentre',
            modo_adquisicion='comprado',
            fecha_adquisicion=date(2026, 1, 1),
        )

    def _payload(self, equipo: Equipo | None = None) -> dict:
        """Retorna una solicitud valida de instalacion."""
        return {
            'equipo_id': (equipo or self.equipo).id,
            'producto_software_id': self.producto.id,
            'numero_licencia_usado': 'LIC-SW-001',
            'fecha_instalacion': date.today().isoformat(),
        }

    def test_endpoints_require_authentication(self):
        """Rechaza el catalogo y las instalaciones sin credenciales."""
        products_response = self.client.get(self.productos_url)
        installations_response = self.client.get(self.instalaciones_url)

        self.assertEqual(products_response.status_code, 401)
        self.assertEqual(installations_response.status_code, 401)

    def test_non_operational_role_cannot_access_software(self):
        """Impide acceso a usuarios que no sean admin ni tecnico."""
        self.client.force_authenticate(self.docente)

        read_response = self.client.get(self.productos_url)
        write_response = self.client.post(
            self.instalaciones_url,
            self._payload(),
            format='json',
        )

        self.assertEqual(read_response.status_code, 403)
        self.assertEqual(write_response.status_code, 403)

    def test_admin_lists_products_with_license_availability(self):
        """Expone el catalogo vigente con el consumo real de licencias."""
        self.client.force_authenticate(self.admin)

        response = self.client.get(
            self.productos_url,
            {'search': 'Ofimatica', 'tipo_licencia': 'volumen'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        product = response.data['results'][0]
        self.assertEqual(product['id'], self.producto.id)
        self.assertEqual(product['licencias_usadas'], 0)
        self.assertEqual(product['licencias_disponibles'], 1)

    def test_tecnico_installs_and_lists_software_by_equipment(self):
        """Permite al tecnico instalar y consultar el software del equipo."""
        self.client.force_authenticate(self.tecnico)

        created = self.client.post(
            self.instalaciones_url,
            self._payload(),
            format='json',
        )
        listed = self.client.get(
            self.instalaciones_url,
            {'equipo_id': self.equipo.id},
        )
        other_equipment = self.client.get(
            self.instalaciones_url,
            {'equipo_id': self.otro_equipo.id},
        )

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['equipo'], self.equipo.id)
        self.assertEqual(created.data['equipo_codigo'], self.equipo.codigo)
        self.assertEqual(created.data['producto']['id'], self.producto.id)
        self.assertEqual(created.data['producto']['version'], '2026')
        self.assertEqual(listed.data['count'], 1)
        self.assertEqual(other_equipment.data['count'], 0)
        installation = SoftwareInstalado.objects.get(id=created.data['id'])
        self.assertEqual(installation.created_by, self.tecnico)

    def test_duplicate_installation_returns_field_error(self):
        """Impide instalar dos veces el mismo producto en un equipo."""
        self.client.force_authenticate(self.admin)
        self.client.post(self.instalaciones_url, self._payload(), format='json')

        response = self.client.post(
            self.instalaciones_url,
            self._payload(),
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('producto_software_id', response.data['errores'])

    def test_license_capacity_is_enforced(self):
        """No excede la cantidad total de licencias contratadas."""
        self.client.force_authenticate(self.admin)
        self.client.post(self.instalaciones_url, self._payload(), format='json')

        response = self.client.post(
            self.instalaciones_url,
            self._payload(self.otro_equipo),
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('producto_software_id', response.data['errores'])

    def test_expired_license_and_future_date_are_rejected(self):
        """Valida vigencia de licencia y que la instalacion ya haya ocurrido."""
        self.client.force_authenticate(self.admin)
        self.producto.fecha_expiracion = date.today() - timedelta(days=1)
        self.producto.save(update_fields=['fecha_expiracion'])

        expired = self.client.post(
            self.instalaciones_url,
            self._payload(),
            format='json',
        )
        self.producto.fecha_expiracion = date.today() + timedelta(days=365)
        self.producto.save(update_fields=['fecha_expiracion'])
        future_payload = {
            **self._payload(),
            'fecha_instalacion': (date.today() + timedelta(days=1)).isoformat(),
        }
        future = self.client.post(
            self.instalaciones_url,
            future_payload,
            format='json',
        )

        self.assertEqual(expired.status_code, 400)
        self.assertIn('producto_software_id', expired.data['errores'])
        self.assertEqual(future.status_code, 400)
        self.assertIn('fecha_instalacion', future.data['errores'])

    def test_delete_is_logical_and_allows_reinstalling(self):
        """Retira sin perder historial y reactiva la misma relacion al reinstalar."""
        self.client.force_authenticate(self.tecnico)
        created = self.client.post(
            self.instalaciones_url,
            self._payload(),
            format='json',
        )
        detail_url = reverse(
            'software-instalado-detail',
            args=[created.data['id']],
        )

        deleted = self.client.delete(detail_url)
        hidden = self.client.get(
            self.instalaciones_url,
            {'equipo_id': self.equipo.id},
        )
        restored = self.client.post(
            self.instalaciones_url,
            {**self._payload(), 'numero_licencia_usado': 'LIC-SW-002'},
            format='json',
        )

        installation = SoftwareInstalado.objects.get(id=created.data['id'])
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(hidden.data['count'], 0)
        self.assertEqual(restored.status_code, 201)
        self.assertEqual(restored.data['id'], created.data['id'])
        self.assertFalse(installation.is_deleted)
        self.assertEqual(installation.numero_licencia_usado, 'LIC-SW-002')

    def test_rejects_retired_equipment_and_product(self):
        """No crea instalaciones con relaciones eliminadas logicamente."""
        self.client.force_authenticate(self.admin)
        self.equipo.is_deleted = True
        self.equipo.save(update_fields=['is_deleted'])

        retired_equipment = self.client.post(
            self.instalaciones_url,
            self._payload(),
            format='json',
        )
        self.equipo.is_deleted = False
        self.equipo.save(update_fields=['is_deleted'])
        self.producto.is_deleted = True
        self.producto.save(update_fields=['is_deleted'])
        retired_product = self.client.post(
            self.instalaciones_url,
            self._payload(),
            format='json',
        )

        self.assertEqual(retired_equipment.status_code, 400)
        self.assertIn('equipo_id', retired_equipment.data['errores'])
        self.assertEqual(retired_product.status_code, 400)
        self.assertIn('producto_software_id', retired_product.data['errores'])
