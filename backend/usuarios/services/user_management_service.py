from usuarios.repositories.user_repository import UserRepository
from usuarios.models import Usuario
from usuarios.exceptions import UsuarioNoEncontrado, DatosInvalidos

class UserManagementService:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository
        
    def list_usuarios(self,) -> list:
        return self.repo.get_all()
    
    def get_usuario(self, user_id: int) -> Usuario:
        usuario = self.repo.get_by_id(user_id)
        if usuario is None:
            raise UsuarioNoEncontrado(f"Usuario {user_id} no encontrado")
        return usuario
    
    def create_usuario(self, datos: dict) -> Usuario:
        if self.repo.get_by_email(datos.get("correo","")):
            raise DatosInvalidos("El correo ya esta registrado")

        return self.repo.create_user(**datos)
    
    def update_usuario(self, user_id: int, datos: dict) -> Usuario:
        usuario = self.get_usuario(user_id)
        
        return self.repo.update_user(usuario, **datos)
    
    def deactivate_usuario(self, user_id: int) -> Usuario:
        usuario = self.get_usuario(user_id)
        return self.repo.soft_delete(usuario)
         
        
    