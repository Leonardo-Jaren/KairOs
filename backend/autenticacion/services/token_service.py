from rest_framework_simplejwt.tokens import RefreshToken
from usuarios.models import Usuario


class TokenService:
    """
    Servicio encargado de encapsular la generación de JSON Web Tokens (JWT) locales.
    Utiliza djangorestframework-simplejwt para generar Access y Refresh tokens.
    """
    def generate_tokens_for_user(self, user: Usuario) -> dict:
        """
        Genera un par de tokens (Access y Refresh) para un usuario específico.
        """
        refresh = RefreshToken.for_user(user)
        
        # Añadimos claims personalizados opcionales en el token
        refresh['rol'] = user.rol
        refresh['nombre'] = user.nombre
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
