from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from shared.base import BasePagination
from shared.utils import parse_integer
from historial.models import Historial
from historial.serializers.historial_serializers import HistorialSerializer
from historial.services.historial_service import HistorialService


class HistorialViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    """
    Expone el log de auditoría en modo solo lectura.
    No hereda BaseViewSet porque el historial no admite escritura — igual que
    autenticacion usa APIView en lugar de BaseViewSet por contrato diferente.
    """

    serializer_class = HistorialSerializer
    pagination_class = BasePagination
    permission_classes = [IsAuthenticated]
    service = HistorialService()
    queryset = Historial.objects.none()

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista eventos del log aplicando filtros opcionales."""
        queryset = self.service.listar(
            modulo=request.query_params.get('modulo'),
            object_id=parse_integer(request.query_params.get('object_id')),
            tipo_evento=request.query_params.get('tipo_evento'),
            usuario_id=parse_integer(request.query_params.get('usuario_id')),
            fecha_desde=request.query_params.get('fecha_desde'),
            fecha_hasta=request.query_params.get('fecha_hasta'),
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Obtiene el detalle de un evento de auditoría por su ID."""
        instance = self.service.get_by_id(kwargs['pk'])
        return Response(self.get_serializer(instance).data)

