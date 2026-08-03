from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from equipos.permissions import CanManageEquipo
from equipos.serializers import EquipoCreateUpdateSerializer, EquipoSerializer
from equipos.services import EquipoService
from shared.base import BaseViewSet


class EquipoViewSet(BaseViewSet):
    """Expone el CRUD y consulta operativa de equipos informaticos."""

    service = EquipoService()
    serializer_class = EquipoSerializer
    permission_classes = [CanManageEquipo]

    def get_serializer_class(self):
        """Selecciona serializers separados para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return EquipoCreateUpdateSerializer
        return EquipoSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista equipos aplicando busqueda, tipo, estado y espacio."""
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            tipo_equipo=request.query_params.get('tipo_equipo', ''),
            estado=request.query_params.get('estado', ''),
            espacio_id=self.parse_integer_query(request.query_params.get('espacio_id')),
        )
        return self.get_collection_response(queryset)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Crea un equipo validando datos de negocio."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data, actor=request.user)
        return Response(EquipoSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza total o parcialmente un equipo existente."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(kwargs['pk'], serializer.validated_data, actor=request.user)
        return Response(EquipoSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Retira un equipo preservando su historial de mantenimientos."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request: Request) -> Response:
        """Entrega indicadores agregados del modulo de equipos."""
        return Response(self.service.get_estadisticas())

    @action(detail=False, methods=['get'], url_path='opciones')
    def opciones(self, request: Request) -> Response:
        """Entrega equipos vigentes para poblar selects de otros modulos."""
        return Response(self.service.get_opciones())
