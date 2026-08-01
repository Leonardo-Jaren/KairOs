from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from autenticacion.services.google_auth_service import GoogleAuthService
from autenticacion.services.token_service import TokenService

Usuario = get_user_model()


class GoogleAuthServiceTests(TestCase):
    """
    Casos de prueba unitarios para GoogleAuthService utilizando mocks
    para evitar peticiones de red reales durante las pruebas.
    """
    def setUp(self):
        self.service = GoogleAuthService(client_id="dummy-client-id")

    def test_verify_token_requires_client_id(self):
        """
        Valida que se lance un error si GOOGLE_CLIENT_ID no está configurado.
        """
        self.service.client_id = ''
        
        with self.assertRaises(ValidationError) as context:
            self.service.verify_token("any-dummy-token")
        self.assertIn("GOOGLE_CLIENT_ID no está configurada", str(context.exception))

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_verify_token_success(self, mock_verify):
        """
        Valida que un token correcto e issuer legítimo retorne los datos esperados.
        """
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
        mock_verify.assert_called_once()
        self.assertEqual(mock_verify.call_args.args[2], 'dummy-client-id')

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_verify_token_invalid_issuer(self, mock_verify):
        """
        Valida que se lance error si el emisor (issuer) no es de confianza.
        """
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

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_verify_token_requires_verified_email(self, mock_verify):
        """Valida que Google haya verificado el correo del perfil."""
        mock_verify.return_value = {
            'iss': 'accounts.google.com',
            'email': 'john.doe@gmail.com',
            'sub': 'google-uid-12345',
            'email_verified': False,
        }

        with self.assertRaises(ValidationError) as context:
            self.service.verify_token("mock-google-id-token")
        self.assertIn("no est", str(context.exception))

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_verify_token_requires_identifiable_profile(self, mock_verify):
        """Valida que el token incluya correo e identificador de Google."""
        mock_verify.return_value = {
            'iss': 'accounts.google.com',
            'email_verified': True,
        }

        with self.assertRaises(ValidationError) as context:
            self.service.verify_token("mock-google-id-token")
        self.assertIn("no contiene un perfil identificable", str(context.exception))


class GoogleLoginViewTests(APITestCase):
    """Pruebas de integracion del endpoint de inicio con Google."""

    endpoint = '/api/v1/auth/google/'

    @patch('autenticacion.views.login_views.GoogleAuthService.verify_token')
    def test_google_login_creates_user_and_returns_local_tokens(self, mock_verify):
        """Crea la cuenta local y devuelve los JWT propios del sistema."""
        mock_verify.return_value = {
            'correo': 'nuevo.usuario@gmail.com',
            'nombre': 'Nuevo Usuario',
            'google_id': 'google-uid-12345',
        }

        response = self.client.post(
            self.endpoint,
            {'token': 'id-token-valido'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['usuario']['correo'], 'nuevo.usuario@gmail.com')
        self.assertTrue(Usuario.objects.filter(correo='nuevo.usuario@gmail.com').exists())

    @patch('autenticacion.views.login_views.GoogleAuthService.verify_token')
    def test_google_login_rejects_inactive_user(self, mock_verify):
        """Impide iniciar sesion a una cuenta local desactivada."""
        Usuario.objects.create(
            correo='inactivo@gmail.com',
            username='inactivo',
            nombre='Usuario Inactivo',
            rol='usuario',
            is_active=False,
        )
        mock_verify.return_value = {
            'correo': 'inactivo@gmail.com',
            'nombre': 'Usuario Inactivo',
            'google_id': 'google-uid-inactivo',
        }

        response = self.client.post(
            self.endpoint,
            {'token': 'id-token-valido'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('autenticacion.views.login_views.GoogleAuthService.verify_token')
    def test_google_login_rejects_invalid_google_token(self, mock_verify):
        """Expone un error controlado cuando Google rechaza el ID token."""
        mock_verify.side_effect = ValidationError('Token de Google invalido.')

        response = self.client.post(
            self.endpoint,
            {'token': 'id-token-invalido'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Token de Google invalido', response.data['detail'])


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


from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from autenticacion.services.password_service import PasswordService

class PasswordServiceTests(TestCase):
    """
    Casos de prueba para el servicio de recuperación de contraseñas.
    """
    def setUp(self):
        self.service = PasswordService()
        self.user = Usuario.objects.create(
            correo="reset.test@example.com",
            username="resetuser",
            nombre="Reset User",
            rol="usuario"
        )
        self.user.set_password("oldpassword123")
        self.user.save()

    def test_request_password_reset_sends_email(self):
        """Valida que solicitar recuperación de contraseña envíe un correo."""
        self.service.request_password_reset("reset.test@example.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Recuperación de contraseña en KairOs")
        self.assertIn("reset.test@example.com", mail.outbox[0].to)
        self.assertIn("reset-password/", mail.outbox[0].body)

    def test_request_password_reset_invalid_email_silent(self):
        """Valida que un correo inexistente no lance error ni envíe correos (seguridad)."""
        self.service.request_password_reset("nonexistent@example.com")
        self.assertEqual(len(mail.outbox), 0)

    def test_validate_token_and_reset_success(self):
        """Valida que con token correcto se actualice la contraseña."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.user)
        
        success = self.service.validate_token_and_reset(uidb64, token, "newpassword123")
        self.assertTrue(success)
        
        # Verificar en base de datos
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_validate_token_and_reset_invalid_token(self):
        """Valida que el servicio rechace tokens inválidos."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        success = self.service.validate_token_and_reset(uidb64, "invalid-token-123", "newpassword123")
        self.assertFalse(success)
        
        # La contraseña antigua debe mantenerse
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword123"))
