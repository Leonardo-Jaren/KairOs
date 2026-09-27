from espacios.models import Ciudad
from shared.base import BaseRepository


class CiudadRepository(BaseRepository):
    """Centraliza las consultas del catálogo de ciudades."""

    model = Ciudad

    def get_all(self):
        return self.model.objects.filter(is_deleted=False).order_by('nombre')

    def get_by_id(self, id: int) -> Ciudad | None:
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def get_by_nombre_normalizado(self, nombre_normalizado: str) -> Ciudad | None:
        return self.model.objects.filter(
            nombre_normalizado=nombre_normalizado,
        ).first()

    def listar(self, busqueda: str = ''):
        queryset = self.get_all()
        if busqueda:
            queryset = queryset.filter(nombre__icontains=busqueda)
        return queryset

    def restaurar(self, ciudad: Ciudad, actor) -> Ciudad:
        ciudad.is_deleted = False
        ciudad.updated_by = actor
        ciudad.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
        return ciudad
