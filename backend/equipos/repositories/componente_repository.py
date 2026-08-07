from equipos.models import Componente, Equipo
from shared.base import BaseRepository


class ComponenteRepository(BaseRepository):
    """Centraliza las consultas y persistencia de componentes de equipos."""

    model = Componente

    def get_all(self):
        return self.model.objects.filter(is_deleted=False).select_related('equipo')

    def get_by_id(self, id: int) -> Componente | None:
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(self, equipo_id: int | None = None):
        qs = self.get_all()
        if equipo_id is not None:
            qs = qs.filter(equipo_id=equipo_id)
        return qs.order_by('tipo', 'modelo')

    def get_equipo_by_id(self, equipo_id: int) -> Equipo | None:
        try:
            return Equipo.objects.get(id=equipo_id, is_deleted=False)
        except Equipo.DoesNotExist:
            return None

    def soft_delete(self, instance: Componente, actor) -> None:
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
