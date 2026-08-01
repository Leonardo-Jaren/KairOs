from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from espacios.permissions import CanManageEspacioUsuario
from espacios.serializers import (
    EspacioUsuarioCreateUpdateSerializer,
    EspacioUsuarioSerializer,
)
from espacios.services import EspacioUsuarioService
from shared.base_viewset import BaseViewSet


class EspacioUsuarioViewSet(BaseViewSet):
    """Expone la gestión de asignaciones entre usuarios y espacios."""

    service = EspacioUsuarioService()
    serializer_class = EspacioUsuarioSerializer
    permission_classes = [CanManageEspacioUsuario]

    def get_serializer_class(self):
        """Usa serializers separados para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return EspacioUsuarioCreateUpdateSerializer
        return EspacioUsuarioSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista asignaciones con filtros de búsqueda y estado."""
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            activo=self.parse_boolean_query(request.query_params.get('activo')),
            usuario_id=self.parse_integer_query(
                request.query_params.get('usuario_id')
            ),
            espacio_id=self.parse_integer_query(
                request.query_params.get('espacio_id')
            ),
        )
        return self.get_collection_response(queryset)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Crea una asignación auditada."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(
            serializer.validated_data,
            actor=request.user,
        )
        return Response(
            EspacioUsuarioSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza total o parcialmente una asignación."""
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
        return Response(EspacioUsuarioSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Elimina lógicamente una asignación."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='opciones')
    def opciones(self, request: Request) -> Response:
        """Entrega opciones de usuarios y espacios para formularios."""
        return Response(self.service.get_opciones())
