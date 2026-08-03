from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from shared.base import BaseService
from historial.models import Historial
from historial.repositories.historial_repository import HistorialRepository


class HistorialService(BaseService):
    """Gestiona el registro y consulta del log de auditoría global."""

    def __init__(self):
        self.repository = HistorialRepository()

    def update(self, id: int, data: dict) -> None:
        """Bloqueado: los registros de historial son inmutables."""
        raise NotImplementedError("Los registros de historial son inmutables.")

    def delete(self, id: int) -> None:
        """Bloqueado: los registros de historial no pueden eliminarse."""
        raise NotImplementedError("Los registros de historial no pueden eliminarse.")

    def registrar(
        self,
        objeto,
        tipo_evento: str,
        descripcion: str,
        usuario=None,
        datos_extra: dict | None = None,
    ) -> Historial:
        """
        Registra un evento de auditoría asociado a cualquier objeto del sistema.
        Se llama exclusivamente desde otros servicios, nunca desde la API.
        """
        content_type = ContentType.objects.get_for_model(objeto)
        return self.repository.registrar(
            content_type=content_type,
            object_id=objeto.pk,
            tipo_evento=tipo_evento,
            descripcion=descripcion,
            usuario=usuario,
            datos_extra=datos_extra,
        )

    def listar(
        self,
        modulo: str | None = None,
        object_id: int | None = None,
        tipo_evento: str | None = None,
        usuario_id: int | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
    ) -> QuerySet:
        """Retorna eventos del log aplicando los filtros indicados."""
        content_type_id = None
        if modulo:
            try:
                ct = ContentType.objects.get(model=modulo.lower())
                content_type_id = ct.id
            except ContentType.DoesNotExist:
                return self.repository.model.objects.none()

        return self.repository.listar(
            content_type_id=content_type_id,
            object_id=object_id,
            tipo_evento=tipo_evento,
            usuario_id=usuario_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
