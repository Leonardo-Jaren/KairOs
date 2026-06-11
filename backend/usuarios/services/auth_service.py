from usuarios.repositories.user_repository import UserRepository
from usuarios.models import Usuario
from usuarios.exceptions import AutenticacionError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError



class AuthService:
    def __init__(self, user_repository: UserRepository):
          self.repo = user_repository
          
    def authenticate(self, correo: str, password: str) -> Usuario:
        """
        Verifica credenciales
        """
        user = self.repo.get_by_email(correo)
        if user is None or not user.check_password(password):
            raise AutenticacionError("Credenciales invalidas")
        if not user.activo:
            raise AutenticacionError("Usuario inactivo")
        
        return user
        
    def generate_tokens(self, user:Usuario) -> dict:
        """
        Genera el token
        """
        refresh = RefreshToken.for_user(user)
        
        refresh["nombre"] = user.nombre
        refresh["rol"] = user.rol
        
        if user.rol == Usuario.Rol.TECNICO:
            profile = self.repo.get_tecnico_profile(user)
            refresh["id_tecnico"] = profile.id_tecnico if profile else None
            
        return {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
        }
            
    def refresh_access_token(self, refresh_token: str) -> dict:
        """Renovacion del access"""
        try: 
            token = RefreshToken(refresh_token)
            return {"access": str(token.access_token)}
        except TokenError:
            raise AutenticacionError("Refresh token invalido o expirado")
        
        
    def logout(self, refresh_token: str)-> None:
        """Cierre de sesion - invalida el refresh token"""
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise AutenticacionError("Token invalido o expirado")
            
        

    