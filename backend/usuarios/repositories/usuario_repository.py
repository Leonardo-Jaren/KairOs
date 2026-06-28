from shared.base_repository import BaseRepository
from usuarios.models import Usuario, PerfilTecnico


class UsuarioRepository(BaseRepository):
    """
    Repositorio encargado del acceso y manipulación de datos de la entidad Usuario.
    Aplica el principio de Responsabilidad Única (SRP) abstrayendo el ORM de Django.
    """
    model = Usuario

    def get_by_correo(self, correo: str) -> Usuario | None:
        """
        Busca un usuario por su correo electrónico.
        """
        try:
            return self.model.objects.get(correo=correo)
        except self.model.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Usuario | None:
        """
        Busca un usuario por su nombre de usuario.
        """
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return None

    def create_user(self, **kwargs) -> Usuario:
        """
        Crea un nuevo usuario gestionando correctamente la contraseña
        e inicializaciones del modelo AbstractUser.
        """
        password = kwargs.pop('password', None)
        user = self.model(**kwargs)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create(self, **kwargs) -> Usuario:
        """
        Sobrescribe el método de creación general para asegurar que
        se delegue a create_user y se encripte la contraseña.
        """
        return self.create_user(**kwargs)

    def update(self, instance: Usuario, **kwargs) -> Usuario:
        """
        Sobrescribe el método de actualización para encriptar la
        contraseña si es provista en los datos de actualización.
        """
        password = kwargs.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, **kwargs)



class PerfilTecnicoRepository(BaseRepository):
    """
    Repositorio encargado del acceso y manipulación de datos del perfil específico de técnicos.
    """
    model = PerfilTecnico

    def get_by_usuario_id(self, usuario_id: int) -> PerfilTecnico | None:
        """
        Obtiene el perfil técnico asociado a un ID de usuario.
        """
        try:
            return self.model.objects.get(usuario_id=usuario_id)
        except self.model.DoesNotExist:
            return None
