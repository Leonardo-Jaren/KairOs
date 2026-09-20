from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from shared.base import BaseViewSet
from usuarios.permissions import CanManageDocentes
from usuarios.serializers import (
    GuardarPermisosSerializer,
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
        local_id = int(request.query_params['local_id']) if request.query_params.get('local_id') else None
        supervisor_id = int(request.query_params['supervisor_id']) if request.query_params.get('supervisor_id') else None
        queryset = self.service.listar(
            actor=request.user,
            busqueda=request.query_params.get('search', ''),
            rol=request.query_params.get('rol', ''),
            activo=activo,
            local_id=local_id,
            supervisor_id=supervisor_id,
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

    @action(detail=False, methods=['get'], url_path='organigrama')
    def organigrama(self, request: Request) -> Response:
        """Devuelve el organigrama estructurado jerárquicamente."""
        local_id = int(request.query_params['local_id']) if request.query_params.get('local_id') else None
        return Response(self.service.get_organigrama(actor=request.user, local_id=local_id))

    @action(detail=True, methods=['get', 'post'], url_path='permisos')
    def permisos(self, request: Request, pk=None) -> Response:
        """Consulta o actualiza la matriz de permisos personalizados de un usuario."""
        instance = self.service.get_by_id(pk)
        self.check_object_permissions(request, instance)

        if request.method == 'GET':
            return Response(self.service.get_permisos(pk, actor=request.user))

        serializer = GuardarPermisosSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('reset_to_default'):
            data = self.service.reset_permisos(pk, actor=request.user)
        else:
            permisos_data = serializer.validated_data.get('permisos', [])
            data = self.service.guardar_permisos(pk, permisos_data, actor=request.user)
        return Response(data)

    @action(detail=True, methods=['get'], url_path='actividad')
    def actividad(self, request: Request, pk=None) -> Response:
        """Retorna los últimos eventos de auditoría del usuario a cargo."""
        instance = self.service.get_by_id(pk)
        self.check_object_permissions(request, instance)
        limit = int(request.query_params.get('limit', 20))
        return Response(self.service.get_actividad(pk, actor=request.user, limit=limit))

    @action(detail=True, methods=['get'], url_path='subordinados')
    def subordinados(self, request: Request, pk=None) -> Response:
        """Retorna subordinados directos asignados al usuario."""
        instance = self.service.get_by_id(pk)
        self.check_object_permissions(request, instance)
        subs = self.service.repository.get_subordinados(pk, directos_solo=True)
        return Response(UsuarioSerializer(subs, many=True).data)


