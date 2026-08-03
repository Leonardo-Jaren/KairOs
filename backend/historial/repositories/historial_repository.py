from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from shared.base import BaseRepository
from historial.models import Historial


class HistorialRepository(BaseRepository):
    """Centraliza el acceso a datos del log de auditoría."""

    model = Historial

    def update(self, instance: Historial, **kwargs) -> None:
        """Bloqueado: los registros de historial son inmutables."""
        raise NotImplementedError("Los registros de historial son inmutables.")

    def delete(self, instance: Historial) -> None:
        """Bloqueado: los registros de historial no pueden eliminarse."""
        raise NotImplementedError("Los registros de historial no pueden eliminarse.")

    def registrar(
        self,
        content_type: ContentType,
        object_id: int,
        tipo_evento: str,
        descripcion: str,
        usuario=None,
        datos_extra: dict | None = None,
    ) -> Historial:
        """Inserta un nuevo evento de auditoría."""
        return self.model.objects.create(
            content_type=content_type,
            object_id=object_id,
            tipo_evento=tipo_evento,
            descripcion=descripcion,
            usuario=usuario,
            datos_extra=datos_extra,
        )

    def listar(
        self,
        content_type_id: int | None = None,
        object_id: int | None = None,
        tipo_evento: str | None = None,
        usuario_id: int | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
    ) -> QuerySet:
        """Retorna eventos filtrados con relaciones pre-cargadas."""
        queryset = (
            self.model.objects
            .select_related('content_type', 'usuario')
            .order_by('-fecha')
        )

        if content_type_id is not None:
            queryset = queryset.filter(content_type_id=content_type_id)
        if object_id is not None:
            queryset = queryset.filter(object_id=object_id)
        if tipo_evento:
            queryset = queryset.filter(tipo_evento__startswith=tipo_evento)
        if usuario_id is not None:
            queryset = queryset.filter(usuario_id=usuario_id)
        if fecha_desde:
            queryset = queryset.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__date__lte=fecha_hasta)

        return queryset
