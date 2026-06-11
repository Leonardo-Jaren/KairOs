from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from software.serializers.producto_serializers import (
    ProductoSoftwareReadSerializer,
    ProductoSoftwareCreateSerializer,
    ProductoSoftwareUpdateSerializer,
)
from software.services.producto_service import ProductoSoftwareService
from software.repositories.producto_repository import ProductoSoftwareRepository
from software.exceptions import ProductoSoftwareNoEncontrado, DatosInvalidos
from usuarios.permissions import EsAdmin, EsAdminOTecnico


class ProductoSoftwareViewSet(viewsets.ViewSet):

    def get_service(self):
        return ProductoSoftwareService(ProductoSoftwareRepository())

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), EsAdminOTecnico()]
        return [IsAuthenticated(), EsAdmin()]

    def list(self, request):
        productos = self.get_service().listar_productos()
        return Response(ProductoSoftwareReadSerializer(productos, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            producto = self.get_service().get_producto(pk)
            return Response(ProductoSoftwareReadSerializer(producto).data)
        except ProductoSoftwareNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = ProductoSoftwareCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            producto = self.get_service().crear_producto(serializer.validated_data)
            return Response(ProductoSoftwareReadSerializer(producto).data, status=status.HTTP_201_CREATED)
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        serializer = ProductoSoftwareUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            producto = self.get_service().actualizar_producto(pk, serializer.validated_data)
            return Response(ProductoSoftwareReadSerializer(producto).data)
        except ProductoSoftwareNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            self.get_service().eliminar_producto(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductoSoftwareNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
