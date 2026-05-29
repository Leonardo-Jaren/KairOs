import os
from django.core.exceptions import ValidationError
from google.oauth2 import id_token
from google.auth.transport import requests


class GoogleAuthService:
    """
    Servicio encargado de la integración con Google Identity Services.
    Valida de forma segura y descentralizada la firma de los tokens emitidos por Google.
    """
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')

    def verify_token(self, token: str) -> dict:
        """
        Verifica criptográficamente el ID Token de Google.
        Retorna los datos de perfil necesarios para la autenticación local.
        """
        if not self.client_id:
            raise ValidationError("La variable de entorno GOOGLE_CLIENT_ID no está configurada en el servidor.")

        try:
            # google.auth.transport.requests.Request() se utiliza para consultar las
            # llaves públicas de Google (las cuales se actualizan periódicamente)
            request = requests.Request()
            
            id_info = id_token.verify_oauth2_token(
                token,
                request,
                self.client_id
            )
            
            # Validar el emisor (issuer)
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError("El emisor del token (issuer) no coincide con Google.")

            # Garantizar que el correo esté verificado
            if not id_info.get('email_verified', False):
                raise ValueError("La dirección de correo de Google no está verificada.")

            return {
                'correo': id_info.get('email'),
                'nombre': id_info.get('name'),
                'google_id': id_info.get('sub'),
            }
        except Exception as e:
            raise ValidationError(f"Verificación fallida del token de Google: {str(e)}")
