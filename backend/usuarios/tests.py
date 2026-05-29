from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from usuarios.models import Usuario
from usuarios.repositories import UsuarioRepository
from usuarios.services import UsuarioService


class UsuarioRepositoryAndServiceTests(TestCase):
    """
    Casos de prueba para verificar la robustez de la capa de datos (Repository)
    y la capa de negocio (Service) en el módulo de usuarios.
    """
    def setUp(self):
        self.repo = UsuarioRepository()
        self.service = UsuarioService()

    def test_create_user_with_password(self):
        """
        Valida la creación correcta de un usuario con contraseña (login local).
        """
        user = self.repo.create_user(
            correo="test@example.com",
            username="testuser",
            nombre="Test User",
            password="securepassword123",
            rol="tecnico"
        )
        self.assertEqual(user.correo, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("securepassword123"))
        self.assertEqual(user.rol, "tecnico")

    def test_create_user_without_password(self):
        """
        Valida que si no se proporciona contraseña (login externo),
        el usuario tenga una contraseña inválida/inutilizable.
        """
        user = self.repo.create_user(
            correo="googleuser@example.com",
            username="googleuser",
            nombre="Google User",
            rol="usuario"
        )
        self.assertFalse(user.has_usable_password())

    def test_get_by_correo(self):
        """
        Valida que la consulta por correo electrónico funcione correctamente.
        """
        self.repo.create_user(
            correo="findme@example.com",
            username="findme",
            nombre="Find Me",
            rol="usuario"
        )
        user = self.repo.get_by_correo("findme@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "findme")

        non_existent = self.repo.get_by_correo("notfound@example.com")
        self.assertIsNone(non_existent)

    def test_create_google_user_resolves_duplicate_username(self):
        """
        Valida que el servicio resuelva colisiones de nombres de usuario
        de forma incremental si varios correos comparten el mismo prefijo.
        """
        # Crear usuario original
        self.repo.create_user(
            correo="juan.original@example.com",
            username="juan",
            nombre="Juan Original",
            rol="usuario"
        )

        # Crear primer usuario de Google chocando con el username 'juan'
        user1 = self.service.create_google_user("juan@example.com", "Juan Google")
        self.assertEqual(user1.username, "juan1")
        self.assertEqual(user1.correo, "juan@example.com")

        # Crear segundo usuario de Google chocando de nuevo
        user2 = self.service.create_google_user("juan@another.com", "Juan Another")
        self.assertEqual(user2.username, "juan2")
        self.assertEqual(user2.correo, "juan@another.com")


class UsuarioViewSetIntegrationTests(APITestCase):
    """
    Pruebas de integración para verificar el correcto funcionamiento del ViewSet de usuarios.
    Valida la serialización de entrada/salida, enrutamiento REST y lógica de validación de negocio.
    """
    def setUp(self):
        self.user = Usuario.objects.create_user(
            correo="admin@example.com",
            username="admin",
            nombre="Admin User",
            password="adminpassword123",
            rol="admin"
        )
        self.list_create_url = reverse('usuario-list')

    def test_list_usuarios(self):
        """
        Valida que se listen los usuarios correctamente sin exponer contraseñas.
        """
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], 'admin')
        self.assertNotIn('password', response.data['results'][0])

    def test_create_usuario_local_success(self):
        """
        Valida el registro de un nuevo usuario por API rest, asegurando que la contraseña se hashee.
        """
        payload = {
            "username": "tecnico1",
            "correo": "tecnico1@example.com",
            "nombre": "Tecnico Uno",
            "rol": "tecnico",
            "password": "techpassword123",
            "is_active": True
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], 'tecnico1')
        self.assertEqual(response.data['correo'], 'tecnico1@example.com')
        
        # Verificar en base de datos
        db_user = Usuario.objects.get(correo="tecnico1@example.com")
        self.assertTrue(db_user.check_password("techpassword123"))

    def test_create_usuario_duplicate_email_fails(self):
        """
        Valida que no se permita registrar un usuario con un correo duplicado a través de la API.
        """
        payload = {
            "username": "anotheradmin",
            "correo": "admin@example.com",  # Duplicado
            "nombre": "Another Admin",
            "rol": "admin",
            "password": "password123"
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('correo', response.data)


