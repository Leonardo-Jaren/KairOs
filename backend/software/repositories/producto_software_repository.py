from django.db.models import Count, Q

from shared.base import BaseRepository
from software.models import ProductoSoftware


class ProductoSoftwareRepository(BaseRepository):
    """Centraliza las consultas del catalogo de productos de software."""

    model = ProductoSoftware

    def get_all(self):
        """Retorna productos vigentes con el consumo actual de licencias."""
        return (
            self.model.objects
            .filter(is_deleted=False)
            .annotate(
                licencias_usadas=Count(
                    'instalaciones',
                    filter=Q(instalaciones__is_deleted=False),
                ),
            )
            .order_by('software', 'version')
        )

    def get_by_id(self, id: int) -> ProductoSoftware | None:
        """Busca un producto vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(self, busqueda: str = '', tipo_licencia: str = ''):
        """Filtra el catalogo por texto y tipo de licencia."""
        queryset = self.get_all()
        if busqueda:
            queryset = queryset.filter(
                Q(software__icontains=busqueda)
                | Q(version__icontains=busqueda)
                | Q(descripcion__icontains=busqueda)
            )
        if tipo_licencia:
            queryset = queryset.filter(tipo_licencia=tipo_licencia)
        return queryset
