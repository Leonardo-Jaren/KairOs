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

    def test_tecnico_only_lists_docentes(self):
        """Restringe la consulta de técnicos a cuentas docentes."""
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

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().rol, 'docente')

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
        }

        response = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(response.status_code, 201)
        created = Usuario.objects.get(correo='docente2@example.com')
        self.assertTrue(created.check_password('TeacherPass456'))
        self.assertNotIn('password', response.data)

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

    def test_tecnico_sees_only_docentes_and_cannot_create_admin(self):
        """Aplica el alcance funcional del rol técnico."""
        self.client.force_authenticate(self.tecnico)

        list_response = self.client.get(self.list_url)
        create_response = self.client.post(
            self.list_url,
            {
                'username': 'forbidden-admin',
                'correo': 'forbidden@example.com',
                'nombre': 'Prohibido',
                'rol': 'admin',
                'password': 'ForbiddenPass123',
            },
            format='json',
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['count'], 1)
        self.assertEqual(list_response.data['results'][0]['rol'], 'docente')
        self.assertEqual(create_response.status_code, 400)
        self.assertIn('rol', create_response.data['errores'])

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

    def test_tecnico_statistics_only_include_docentes(self):
        """No expone al técnico métricas de roles fuera de su alcance."""
        self.client.force_authenticate(self.tecnico)

        response = self.client.get(reverse('usuario-estadisticas'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['docentes'], 1)
        self.assertEqual(response.data['administradores'], 0)

    def test_delete_soft_deactivates_user(self):
        """Desactiva la cuenta desde la API sin eliminar el registro."""
        self.client.force_authenticate(self.admin)

        response = self.client.delete(
            reverse('usuario-detail', args=[self.docente.id])
        )
        self.docente.refresh_from_db()

        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.docente.is_active)
