from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from autenticacion.services.google_auth_service import GoogleAuthService
from autenticacion.services.token_service import TokenService

Usuario = get_user_model()


class GoogleAuthServiceTests(TestCase):
    """
    Casos de prueba unitarios para GoogleAuthService utilizando mocks
    para evitar peticiones de red reales durante las pruebas.
    """
    def setUp(self):
        self.service = GoogleAuthService()

    @patch('autenticacion.services.google_auth_service.os.getenv')
    def test_verify_token_requires_client_id(self, mock_getenv):
        """
        Valida que se lance un error si GOOGLE_CLIENT_ID no está configurado.
        """
        mock_getenv.return_value = None
        self.service.client_id = None
        
        with self.assertRaises(ValidationError) as context:
            self.service.verify_token("any-dummy-token")
        self.assertIn("GOOGLE_CLIENT_ID no está configurada", str(context.exception))

    @patch('google.oauth2.id_token.verify_oauth2_token')
    @patch('autenticacion.services.google_auth_service.os.getenv')
    def test_verify_token_success(self, mock_getenv, mock_verify):
        """
        Valida que un token correcto e issuer legítimo retorne los datos esperados.
        """
        mock_getenv.return_value = "dummy-client-id"
        self.service.client_id = "dummy-client-id"
        
        mock_verify.return_value = {
            'iss': 'https://accounts.google.com',
            'email': 'john.doe@gmail.com',
            'name': 'John Doe',
            'sub': 'google-uid-12345',
            'email_verified': True
        }
        
        profile = self.service.verify_token("mock-google-id-token")
        self.assertEqual(profile['correo'], 'john.doe@gmail.com')
        self.assertEqual(profile['nombre'], 'John Doe')
        self.assertEqual(profile['google_id'], 'google-uid-12345')

    @patch('google.oauth2.id_token.verify_oauth2_token')
    @patch('autenticacion.services.google_auth_service.os.getenv')
    def test_verify_token_invalid_issuer(self, mock_getenv, mock_verify):
        """
        Valida que se lance error si el emisor (issuer) no es de confianza.
        """
        mock_getenv.return_value = "dummy-client-id"
        self.service.client_id = "dummy-client-id"
        
        mock_verify.return_value = {
            'iss': 'https://malicious-issuer.com',
            'email': 'john.doe@gmail.com',
            'name': 'John Doe',
            'sub': 'google-uid-12345',
            'email_verified': True
        }
        
        with self.assertRaises(ValidationError) as context:
            self.service.verify_token("mock-google-id-token")
        self.assertIn("El emisor del token (issuer) no coincide con Google", str(context.exception))


class TokenServiceTests(TestCase):
    """
    Casos de prueba unitarios para TokenService de SimpleJWT.
    """
    def setUp(self):
        self.service = TokenService()

    def test_generate_tokens_for_user(self):
        """
        Valida que se generen tokens JWT válidos para un usuario, incluyendo claims.
        """
        # Crear un usuario de prueba en base de datos temporal de pruebas
        user = Usuario.objects.create(
            correo="token.test@example.com",
            username="tokentest",
            nombre="Token Test",
            rol="usuario"
        )
        user.set_password("mypassword123")
        user.save()

        tokens = self.service.generate_tokens_for_user(user)
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertTrue(isinstance(tokens['access'], str))
        self.assertTrue(isinstance(tokens['refresh'], str))
