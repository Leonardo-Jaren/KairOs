from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from espacios.permissions import CanManageEdificio
from espacios.serializers import LocalCreateUpdateSerializer, LocalSerializer
from espacios.services import LocalService
from shared.base import BaseViewSet


class LocalViewSet(BaseViewSet):
    """Expone el CRUD paginado de locales físicos."""

    service = LocalService()
    serializer_class = LocalSerializer
    permission_classes = [CanManageEdificio]

    def get_serializer_class(self):
        """Separa validación de escritura de la representación de consulta."""
        if self.action in ['create', 'update', 'partial_update']:
            return LocalCreateUpdateSerializer
        return LocalSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista locales aplicando búsqueda y estado."""
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            activo=self.parse_boolean_query(request.query_params.get('activo')),
            actor=request.user,
            solo_asignables=(
                self.parse_boolean_query(request.query_params.get('asignables')) is True
            ),
        )
        return self.get_collection_response(queryset)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Obtiene un local vigente por identificador."""
        instance = self.service.get_by_id(kwargs['pk'])
        return Response(LocalSerializer(instance).data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Registra un local y conserva el actor de auditoría."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data, actor=request.user)
        return Response(LocalSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza un local existente, completo o parcialmente."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(
            kwargs['pk'], serializer.validated_data, actor=request.user
        )
        return Response(LocalSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Retira un local cuando no conserva edificios vigentes."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
