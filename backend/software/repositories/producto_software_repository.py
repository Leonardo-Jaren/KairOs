from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from shared.base import BaseRepository
from software.models import ProductoSoftware


class ProductoSoftwareRepository(BaseRepository):
    """Centraliza las consultas y persistencia del catalogo de software."""

    model = ProductoSoftware

    def get_all(self):
        """Retorna productos de software vigentes."""
        return self.model.objects.filter(is_deleted=False)

    def get_by_id(self, id: int) -> ProductoSoftware | None:
        """Busca un producto de software vigente por identificador."""
        try:
            return self.get_all().get(id=id)
        except self.model.DoesNotExist:
            return None

    def listar(self, busqueda: str = '', tipo_licencia: str = ''):
        """Aplica los filtros disponibles en la pantalla de software."""
        queryset = self.get_all()

        if busqueda:
            queryset = queryset.filter(
                Q(software__icontains=busqueda) | Q(version__icontains=busqueda)
            )
        if tipo_licencia:
            queryset = queryset.filter(tipo_licencia=tipo_licencia)

        return queryset

    def get_by_nombre_version(
        self, software: str, version: str, exclude_id: int | None = None
    ) -> ProductoSoftware | None:
        """Busca un producto por software+version incluyendo registros eliminados."""
        queryset = self.model.objects.filter(
            software__iexact=software, version__iexact=version
        )
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        return queryset.first()

    def get_estadisticas(self) -> dict:
        """Calcula indicadores generales del catalogo de software."""
        productos = self.get_all()
        limite = timezone.localdate() + timedelta(days=ProductoSoftware.DIAS_ALERTA_EXPIRACION)
        licencias_por_expirar = productos.filter(
            fecha_expiracion__isnull=False,
            fecha_expiracion__lte=limite,
            fecha_expiracion__gte=timezone.localdate(),
        ).count()
        sobre_uso = sum(1 for producto in productos if producto.licencias_disponibles < 0)

        return {
            'total_productos': productos.count(),
            'licencias_por_expirar': licencias_por_expirar,
            'productos_sobre_uso': sobre_uso,
        }

    def get_opciones(self):
        """Retorna productos de software vigentes para poblar selects."""
        return list(
            self.get_all()
            .order_by('software', 'version')
            .values('id', 'software', 'version', 'tipo_licencia')
        )

    def soft_delete(self, instance: ProductoSoftware, actor) -> None:
        """Elimina logicamente el producto de software."""
        instance.is_deleted = True
        instance.updated_by = actor
        instance.save(update_fields=['is_deleted', 'updated_by', 'updated_at'])
