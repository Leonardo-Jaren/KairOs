from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from shared.base import BaseViewSet
from software.permissions import CanManageSoftware
from software.serializers import ProductoSoftwareCreateUpdateSerializer, ProductoSoftwareSerializer
from software.services import ProductoSoftwareService


class ProductoSoftwareViewSet(BaseViewSet):
    """Expone el CRUD y consulta operativa del catalogo de software."""

    service = ProductoSoftwareService()
    serializer_class = ProductoSoftwareSerializer
    permission_classes = [CanManageSoftware]

    def get_serializer_class(self):
        """Selecciona serializers separados para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return ProductoSoftwareCreateUpdateSerializer
        return ProductoSoftwareSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista productos de software aplicando busqueda y tipo de licencia."""
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            tipo_licencia=request.query_params.get('tipo_licencia', ''),
        )
        return self.get_collection_response(queryset)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Crea un producto de software validando datos de negocio."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data, actor=request.user)
        return Response(ProductoSoftwareSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza total o parcialmente un producto de software existente."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(kwargs['pk'], serializer.validated_data, actor=request.user)
        return Response(ProductoSoftwareSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Elimina logicamente un producto de software sin instalaciones vigentes."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request: Request) -> Response:
        """Entrega indicadores agregados del catalogo de software."""
        return Response(self.service.get_estadisticas())

    @action(detail=False, methods=['get'], url_path='opciones')
    def opciones(self, request: Request) -> Response:
        """Entrega productos de software vigentes para poblar selects de otros modulos."""
        return Response(self.service.get_opciones())
