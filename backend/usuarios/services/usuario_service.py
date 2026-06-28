from shared.base_service import BaseService
from usuarios.repositories.usuario_repository import UsuarioRepository
from usuarios.models import Usuario


class UsuarioService(BaseService):
    """
    Servicio de lógica de negocio para la gestión de usuarios.
    Sigue el principio de Inversión de Dependencias (DIP) interactuando
    con la base de datos únicamente a través de la interfaz de UsuarioRepository.
    """
    def __init__(self):
        self.repository = UsuarioRepository()

    def get_by_correo(self, correo: str) -> Usuario | None:
        """
        Obtiene un usuario por su correo electrónico.
        """
        return self.repository.get_by_correo(correo)

    def create_google_user(self, correo: str, nombre: str) -> Usuario:
        """
        Crea dinámicamente un usuario autenticado externamente por Google.
        Genera un 'username' único basado en el correo electrónico de Gmail.
        """
        # Generar un nombre de usuario inicial a partir del correo
        base_username = correo.split('@')[0]
        username = base_username
        
        # Resolver colisiones en el username añadiendo un contador incremental
        counter = 1
        while self.repository.exists(username=username):
            username = f"{base_username}{counter}"
            counter += 1

        # Crear el usuario en la base de datos con contraseña inutilizable
        user = self.repository.create_user(
            correo=correo,
            username=username,
            nombre=nombre,
            rol='usuario',
            is_active=True
        )
        return user
