from django.db.models import Q

from shared.base import BaseRepository
from software.models import SoftwareInstalado


class SoftwareInstaladoRepository(BaseRepository):
    """Centraliza las consultas y persistencia de instalaciones de software."""

    model = SoftwareInstalado

    def get_all(self):
        """Retorna instalaciones vigentes con equipo, espacio y producto precargados."""
        return self.model.objects.filter(is_deleted=False).select_related(
            'equipo', 'equipo__espacio', 'producto_software'
        )

    def get_by_id(self, id: int) -> SoftwareInstalado | None:
        """Busca una instalacion vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(
        self,
        busqueda: str = '',
        equipo_id: int | None = None,
        espacio_id: int | None = None,
        producto_software_id: int | None = None,
    ):
        """Aplica los filtros disponibles en la pantalla de instalaciones."""
        queryset = self.get_all()

        if busqueda:
            queryset = queryset.filter(
                Q(producto_software__software__icontains=busqueda)
                | Q(equipo__codigo__icontains=busqueda)
                | Q(numero_licencia_usado__icontains=busqueda)
            )
        if equipo_id is not None:
            queryset = queryset.filter(equipo_id=equipo_id)
        if espacio_id is not None:
            queryset = queryset.filter(equipo__espacio_id=espacio_id)
        if producto_software_id is not None:
            queryset = queryset.filter(producto_software_id=producto_software_id)

        return queryset

    def get_by_equipo_producto(
        self, equipo_id: int, producto_software_id: int, exclude_id: int | None = None
    ) -> SoftwareInstalado | None:
        """Busca una instalacion por equipo+producto incluyendo registros eliminados."""
        queryset = self.model.objects.filter(
            equipo_id=equipo_id, producto_software_id=producto_software_id
        )
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def soft_delete(self, instance: SoftwareInstalado, actor) -> None:
        """Elimina logicamente la instalacion, liberando una licencia disponible."""
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
