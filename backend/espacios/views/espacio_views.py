from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from espacios.permissions import CanManageEspacio
from espacios.serializers import (
    DisposicionEspacioSerializer,
    EspacioCreateUpdateSerializer,
    EspacioDetailSerializer,
    EspacioSerializer,
)
from espacios.services import EspacioService
from shared.base import BaseViewSet


class EspacioViewSet(BaseViewSet):
    """Expone el CRUD y consulta operativa de espacios."""

    service = EspacioService()
    serializer_class = EspacioSerializer
    permission_classes = [CanManageEspacio]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EspacioCreateUpdateSerializer
        if self.action == 'retrieve':
            return EspacioDetailSerializer
        return EspacioSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            tipo=request.query_params.get('tipo', ''),
            activo=self.parse_boolean_query(request.query_params.get('activo')),
            pabellon=request.query_params.get('pabellon', ''),
        )
        return self.get_collection_response(queryset)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.service.get_by_id(kwargs['pk'])
        return Response(EspacioDetailSerializer(instance).data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(
            serializer.validated_data,
            actor=request.user,
        )
        return Response(
            EspacioSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
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
        return Response(EspacioSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request: Request) -> Response:
        """Entrega indicadores agregados de espacios."""
        return Response(self.service.get_estadisticas())

    @action(detail=True, methods=['patch'], url_path='disposicion')
    def disposicion(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza la cuadrícula y la posición visual de los equipos."""
        serializer = DisposicionEspacioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = self.service.actualizar_disposicion(
            kwargs['pk'],
            serializer.validated_data,
            actor=request.user,
        )
        return Response(EspacioDetailSerializer(updated).data)
