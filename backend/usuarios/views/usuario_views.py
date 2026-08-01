from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from shared.base_viewset import BaseViewSet
from usuarios.permissions import CanManageDocentes
from usuarios.serializers import (
    UsuarioCreateUpdateSerializer,
    UsuarioSerializer,
)
from usuarios.services import UsuarioService


class UsuarioViewSet(BaseViewSet):
    """Expone la administración de cuentas mediante la capa de servicios."""

    service = UsuarioService()
    serializer_class = UsuarioSerializer
    permission_classes = [CanManageDocentes]

    def get_serializer_class(self):
        """Selecciona serializers separados para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioCreateUpdateSerializer
        return UsuarioSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista usuarios aplicando búsqueda, rol, estado y alcance del actor."""
        activo = self.parse_boolean_query(request.query_params.get('activo'))
        queryset = self.service.listar(
            actor=request.user,
            busqueda=request.query_params.get('search', ''),
            rol=request.query_params.get('rol', ''),
            activo=activo,
        )
        return self.get_collection_response(queryset)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Obtiene una cuenta y verifica permisos sobre el objeto."""
        instance = self.service.get_by_id(kwargs['pk'])
        self.check_object_permissions(request, instance)
        return Response(UsuarioSerializer(instance).data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Crea una cuenta usando validaciones de formato y negocio."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(
            serializer.validated_data,
            actor=request.user,
        )
        return Response(
            UsuarioSerializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza total o parcialmente una cuenta existente."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        self.check_object_permissions(request, instance)
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
        return Response(UsuarioSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Desactiva una cuenta preservando su trazabilidad."""
        instance = self.service.get_by_id(kwargs['pk'])
        self.check_object_permissions(request, instance)
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request: Request) -> Response:
        """Entrega indicadores resumidos para el encabezado del módulo."""
        return Response(self.service.get_estadisticas(actor=request.user))
