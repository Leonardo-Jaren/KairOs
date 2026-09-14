from django.db.models import Q

from espacios.models import Edificio, Local
from shared.base import BaseRepository
from usuarios.models import Usuario


class LocalRepository(BaseRepository):
    """Centraliza consultas y persistencia de locales físicos."""

    model = Local

    def get_all(self):
        """Retorna locales no eliminados lógicamente."""
        return self.model.objects.filter(is_deleted=False).order_by('nombre', 'codigo')

    def get_by_id(self, id: int) -> Local | None:
        """Busca un local vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(self, busqueda: str = '', activo: bool | None = None):
        """Aplica búsqueda por código, nombre, ciudad o descripción."""
        queryset = self.get_all()
        if busqueda:
            queryset = queryset.filter(
                Q(codigo__icontains=busqueda)
                | Q(nombre__icontains=busqueda)
                | Q(ciudad__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
            )
        if activo is not None:
            queryset = queryset.filter(activo=activo)
        return queryset

    def get_by_codigo(self, codigo: str, exclude_id: int | None = None) -> Local | None:
        """Busca un código incluyendo locales retirados."""
        queryset = self.model.objects.filter(codigo__iexact=codigo)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def tiene_edificios_vigentes(self, local: Local) -> bool:
        """Indica si el local aún tiene edificios no eliminados relacionados."""
        return Edificio.objects.filter(local=local, is_deleted=False).exists()

    def soft_delete(self, instance: Local, actor: Usuario) -> None:
        """Retira el local conservando sus relaciones históricas."""
        instance.activo = False
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['activo', 'is_deleted', 'updated_by', 'updated_at'])

    def restore(self, instance: Local, data: dict, actor: Usuario) -> Local:
        """Restaura un local retirado con los datos proporcionados."""
        for field, value in data.items():
            setattr(instance, field, value)
        instance.activo = data.get('activo', True)
        instance.is_deleted = False
        instance.updated_by = actor
        instance.save()
        return self.get_by_id(instance.id)
