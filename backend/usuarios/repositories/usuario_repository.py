from django.db.models import Count, Q

from shared.base_repository import BaseRepository
from usuarios.models import PerfilTecnico, Usuario


class UsuarioRepository(BaseRepository):
    """Centraliza todas las consultas y escrituras de usuarios."""

    model = Usuario

    def get_by_correo(self, correo: str) -> Usuario | None:
        """Busca un usuario por su correo electrónico normalizado."""
        try:
            return self.model.objects.get(correo__iexact=correo.strip())
        except self.model.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Usuario | None:
        """Busca un usuario por su nombre de usuario."""
        try:
            return self.model.objects.get(username__iexact=username.strip())
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        rol: str = '',
        activo: bool | None = None,
        solo_docentes: bool = False,
    ):
        """Retorna usuarios filtrados para la pantalla de administración."""
        queryset = self.model.objects.all().order_by('-id')

        if solo_docentes:
            queryset = queryset.filter(rol='docente')
        elif rol:
            queryset = queryset.filter(rol=rol)

        if activo is not None:
            queryset = queryset.filter(is_active=activo)

        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda)
                | Q(apellido__icontains=busqueda)
                | Q(correo__icontains=busqueda)
                | Q(username__icontains=busqueda)
                | Q(dni__icontains=busqueda)
            )

        return queryset

    def correo_exists(self, correo: str, exclude_id: int | None = None) -> bool:
        """Indica si el correo ya pertenece a otro usuario."""
        queryset = self.model.objects.filter(correo__iexact=correo.strip())
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    def username_exists(self, username: str, exclude_id: int | None = None) -> bool:
        """Indica si el nombre de usuario ya pertenece a otra cuenta."""
        queryset = self.model.objects.filter(username__iexact=username.strip())
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.exists()

    def create_user(self, **kwargs) -> Usuario:
        """Crea una cuenta asegurando el tratamiento correcto de la contraseña."""
        password = kwargs.pop('password', None)
        user = self.model(**kwargs)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create(self, **kwargs) -> Usuario:
        """Delega la creación genérica al flujo seguro de usuarios."""
        return self.create_user(**kwargs)

    def update(self, instance: Usuario, **kwargs) -> Usuario:
        """Actualiza una cuenta y cifra una nueva contraseña cuando se recibe."""
        password = kwargs.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, **kwargs)

    def deactivate(self, instance: Usuario) -> Usuario:
        """Desactiva una cuenta conservando su historial y relaciones."""
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])
        return instance

    def get_estadisticas(self, solo_docentes: bool = False) -> dict:
        """Calcula métricas resumidas para la pantalla de usuarios."""
        queryset = self.model.objects.all()
        if solo_docentes:
            queryset = queryset.filter(rol='docente')
        return queryset.aggregate(
            total=Count('id'),
            activos=Count('id', filter=Q(is_active=True)),
            administradores=Count('id', filter=Q(rol='admin')),
            tecnicos=Count('id', filter=Q(rol='tecnico')),
            docentes=Count('id', filter=Q(rol='docente')),
        )


class PerfilTecnicoRepository(BaseRepository):
    """Gestiona el acceso a datos de los perfiles técnicos."""

    model = PerfilTecnico

    def get_by_usuario_id(self, usuario_id: int) -> PerfilTecnico | None:
        """Obtiene el perfil técnico asociado a un usuario."""
        try:
            return self.model.objects.get(usuario_id=usuario_id)
        except self.model.DoesNotExist:
            return None
