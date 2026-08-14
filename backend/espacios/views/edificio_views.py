from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from espacios.permissions import CanManageEdificio
from espacios.serializers import (
    EdificioCreateUpdateSerializer,
    EdificioSerializer,
)
from espacios.services import EdificioService
from shared.base import BaseViewSet


class EdificioViewSet(BaseViewSet):
    """Expone el CRUD y los indicadores de edificios."""

    service = EdificioService()
    serializer_class = EdificioSerializer
    permission_classes = [CanManageEdificio]

    def get_serializer_class(self):
        """Separa el contrato de escritura de la representación de lectura."""
        if self.action in ['create', 'update', 'partial_update']:
            return EdificioCreateUpdateSerializer
        return EdificioSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista edificios aplicando búsqueda y estado."""
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            activo=self.parse_boolean_query(request.query_params.get('activo')),
        )
        return self.get_collection_response(queryset)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Obtiene un edificio con sus contadores de espacios."""
        instance = self.service.get_by_id(kwargs['pk'])
        return Response(EdificioSerializer(instance).data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Registra un edificio y sus datos de auditoría."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(
            serializer.validated_data,
            actor=request.user,
        )
        return Response(
            EdificioSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza total o parcialmente un edificio."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(
            kwargs['pk'],
            serializer.validated_data,
            actor=request.user,
        )
        return Response(EdificioSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Desactiva un edificio sin eliminar sus espacios."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request: Request) -> Response:
        """Entrega indicadores agregados del campus."""
        return Response(self.service.get_estadisticas())
