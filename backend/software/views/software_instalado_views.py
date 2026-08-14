from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from shared.base import BaseViewSet
from software.permissions import CanManageSoftware
from software.serializers import (
    SoftwareInstaladoCreateSerializer,
    SoftwareInstaladoSerializer,
)
from software.services import SoftwareInstaladoService


class SoftwareInstaladoViewSet(BaseViewSet):
    """Expone la consulta, instalacion y retiro de software por equipo."""

    service = SoftwareInstaladoService()
    serializer_class = SoftwareInstaladoSerializer
    permission_classes = [CanManageSoftware]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """Separa el contrato de asignacion de la representacion de lectura."""
        if self.action == 'create':
            return SoftwareInstaladoCreateSerializer
        return SoftwareInstaladoSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista instalaciones y permite filtrarlas por equipo_id."""
        equipo_id = self.parse_integer_query(
            request.query_params.get('equipo_id'),
        )
        queryset = self.service.listar(equipo_id=equipo_id)
        return self.get_collection_response(queryset)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Instala un producto disponible en el equipo indicado."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(
            serializer.validated_data,
            actor=request.user,
        )
        return Response(
            SoftwareInstaladoSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Retira logicamente una instalacion existente."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
