from django.db.models import Q

from espacios.models import Espacio, EspacioUsuario
from shared.base import BaseRepository
from usuarios.models import Usuario


class EspacioUsuarioRepository(BaseRepository):
    """Centraliza el acceso a datos de asignaciones usuario–espacio."""

    model = EspacioUsuario

    def get_all(self):
        """Retorna asignaciones vigentes con sus relaciones precargadas."""
        return self.model.objects.filter(is_deleted=False).select_related(
            'usuario',
            'espacio',
        )

    def get_by_id(self, id: int) -> EspacioUsuario | None:
        """Busca una asignación vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        activo: bool | None = None,
        usuario_id: int | None = None,
        espacio_id: int | None = None,
    ):
        """Filtra asignaciones para la pantalla de gestión."""
        queryset = self.get_all()
        if activo is not None:
            queryset = queryset.filter(activo=activo)
        if usuario_id is not None:
            queryset = queryset.filter(usuario_id=usuario_id)
        if espacio_id is not None:
            queryset = queryset.filter(espacio_id=espacio_id)
        if busqueda:
            queryset = queryset.filter(
                Q(usuario__nombre__icontains=busqueda)
                | Q(usuario__apellido__icontains=busqueda)
                | Q(usuario__correo__icontains=busqueda)
                | Q(espacio__codigo_espacio__icontains=busqueda)
                | Q(espacio__pabellon__icontains=busqueda)
            )
        return queryset

    def get_by_pair(
        self,
        espacio_id: int,
        usuario_id: int,
        exclude_id: int | None = None,
    ) -> EspacioUsuario | None:
        """Busca una relación por la combinación de espacio y usuario."""
        queryset = self.model.objects.filter(
            espacio_id=espacio_id,
            usuario_id=usuario_id,
        )
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def get_usuario_by_id(self, usuario_id: int) -> Usuario | None:
        """Obtiene una cuenta activa disponible para asignación."""
        try:
            return Usuario.objects.get(id=usuario_id, is_active=True)
        except Usuario.DoesNotExist:
            return None

    def get_espacio_by_id(self, espacio_id: int) -> Espacio | None:
        """Obtiene un espacio vigente disponible para asignación."""
        try:
            return Espacio.objects.get(id=espacio_id, is_deleted=False)
        except Espacio.DoesNotExist:
            return None

    def get_opciones(self) -> dict:
        """Retorna opciones mínimas para formularios de asignación."""
        usuarios = list(
            Usuario.objects.filter(is_active=True)
            .order_by('nombre', 'apellido')
            .values('id', 'nombre', 'apellido', 'correo', 'rol')
        )
        espacios = list(
            Espacio.objects.filter(is_deleted=False)
            .order_by('codigo_espacio')
            .values('id', 'codigo_espacio', 'tipo', 'pabellon', 'piso')
        )
        return {'usuarios': usuarios, 'espacios': espacios}

    def soft_delete(self, instance: EspacioUsuario, actor: Usuario) -> None:
        """Marca una asignación como eliminada conservando auditoría."""
        instance.activo = False
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(
            update_fields=['activo', 'is_deleted', 'updated_by', 'updated_at']
        )

    def restore(
        self,
        instance: EspacioUsuario,
        tipo_responsabilidad: str,
        actor: Usuario,
    ) -> EspacioUsuario:
        """Reactiva una asignación retirada conservando su identidad."""
        instance.tipo_responsabilidad = tipo_responsabilidad
        instance.activo = True
        instance.is_deleted = False
        instance.updated_by = actor
        instance.save(
            update_fields=[
                'tipo_responsabilidad',
                'activo',
                'is_deleted',
                'updated_by',
                'updated_at',
            ]
        )
        return instance
