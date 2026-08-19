from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from equipos.permissions import CanManageEquipo
from equipos.serializers import ComponenteCreateUpdateSerializer, ComponenteSerializer
from equipos.services import ComponenteService
from shared.base import BaseViewSet


class ComponenteViewSet(BaseViewSet):
    """Expone el CRUD de componentes asociados a un equipo."""

    service = ComponenteService()
    serializer_class = ComponenteSerializer
    permission_classes = [CanManageEquipo]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ComponenteCreateUpdateSerializer
        return ComponenteSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista componentes filtrando por equipo, texto y tipo."""
        equipo_id = self.parse_integer_query(request.query_params.get('equipo_id'))
        queryset = self.service.listar(
            equipo_id=equipo_id,
            busqueda=request.query_params.get('search', ''),
            tipo=request.query_params.get('tipo', ''),
        )
        return self.get_collection_response(queryset)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Agrega un componente al equipo indicado."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data, actor=request.user)
        return Response(ComponenteSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza total o parcialmente un componente existente."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(kwargs['pk'], serializer.validated_data, actor=request.user)
        return Response(ComponenteSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Elimina lógicamente un componente."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
