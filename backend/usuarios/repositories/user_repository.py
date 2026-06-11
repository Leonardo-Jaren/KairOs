from typing import Optional
from usuarios.models import PerfilTecnico, Usuario
from usuarios.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[Usuario]):
    def __init__(self):
        ##Decimos con que modelo vamos a trabajar
        super().__init__(Usuario)
        
    def get_all(self):
        return Usuario.objects.all().order_by("id_usuario")
    
    def get_by_id(self, user_id: int) -> Optional[Usuario]:
        return Usuario.objects.filter(id_usuario=user_id).first()
    
    @staticmethod
    def get_by_email(correo: str) -> Optional[Usuario]:
        return Usuario.objects.filter(correo=correo.lower().strip()).first()

    @staticmethod
    def create_user(**validated_data) -> Usuario:
        password = validated_data.pop("password", None)
        return Usuario.objects.create_user(password = password, **validated_data)
    
    @staticmethod
    def update_user(user: Usuario, **validated_data) -> Usuario:
        password = validated_data.pop("password", None)
        
        for field, value in validated_data.items():
            setattr(user, field, value)
            
        if password:
            user.set_password(password)
        
        user.save()
        return user  
        
    @staticmethod
    def soft_delete(user: Usuario) -> Usuario:
        user.activo = False
        user.save(update_fields=["activo","updated_at"])
        return user
        
    def get_tecnico_profile(self,user: Usuario) -> Optional[PerfilTecnico]:
        return PerfilTecnico.objects.filter(usuario=user).first()
    
    
        