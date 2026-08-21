from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from shared.base import BaseViewSet
from software.permissions import CanManageSoftware
from software.serializers import SoftwareInstaladoCreateUpdateSerializer, SoftwareInstaladoSerializer
from software.services import SoftwareInstaladoService


class SoftwareInstaladoViewSet(BaseViewSet):
    """Expone el CRUD y consulta operativa de instalaciones de software."""

    service = SoftwareInstaladoService()
    serializer_class = SoftwareInstaladoSerializer
    permission_classes = [CanManageSoftware]

    def get_serializer_class(self):
        """Selecciona serializers separados para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return SoftwareInstaladoCreateUpdateSerializer
        return SoftwareInstaladoSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista instalaciones aplicando busqueda, equipo, espacio y producto."""
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            equipo_id=self.parse_integer_query(request.query_params.get('equipo_id')),
            espacio_id=self.parse_integer_query(request.query_params.get('espacio_id')),
            producto_software_id=self.parse_integer_query(
                request.query_params.get('producto_software_id')
            ),
        )
        return self.get_collection_response(queryset)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Crea una instalacion de software validando licencias disponibles."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data, actor=request.user)
        return Response(SoftwareInstaladoSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza numero de licencia y fecha de instalacion de una instalacion existente."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(kwargs['pk'], serializer.validated_data, actor=request.user)
        return Response(SoftwareInstaladoSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Elimina logicamente una instalacion, liberando una licencia disponible."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
