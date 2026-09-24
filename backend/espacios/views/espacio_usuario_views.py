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
from shared.base import BaseViewSet


class EspacioUsuarioViewSet(BaseViewSet):
    """Expone la gestión de asignaciones territoriales entre usuarios y ámbitos físicos."""

    service = EspacioUsuarioService()
    serializer_class = EspacioUsuarioSerializer
    permission_classes = [CanManageEspacioUsuario]

    def get_serializer_class(self):
        """Usa serializers separados para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return EspacioUsuarioCreateUpdateSerializer
        return EspacioUsuarioSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista asignaciones con filtros de búsqueda, estado, ámbito y ubicación territorial."""
        actor = request.user
        sede_ids = None

        # Si el usuario es responsable, técnico o docente, acotar la consulta a sus sedes vigentes (R5).
        # Un operador con 0 sedes asignadas debe recibir una lista vacía (sede_ids=[]).
        if actor and actor.is_authenticated and actor.rol not in ('superadmin', 'admin') and not actor.is_superuser:
            sede_ids = list(actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True))

        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            activo=self.parse_boolean_query(request.query_params.get('activo')),
            usuario_id=self.parse_integer_query(
                request.query_params.get('usuario_id')
            ),
            espacio_id=self.parse_integer_query(
                request.query_params.get('espacio_id')
            ),
            ambito=request.query_params.get('ambito', '').strip() or None,
            local_id=self.parse_integer_query(
                request.query_params.get('local_id')
            ),
            edificio_id=self.parse_integer_query(
                request.query_params.get('edificio_id')
            ),
            piso=request.query_params.get('piso', '').strip() or None,
            sede_ids=sede_ids,
            ordering=request.query_params.get('ordering', '').strip() or None,
        )
        return self.get_collection_response(queryset)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Crea una asignación territorial auditada."""
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
        return Response(EspacioUsuarioSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Elimina lógicamente una asignación conservando trazabilidad."""
        instance = self.service.get_by_id(kwargs['pk'])
        self.check_object_permissions(request, instance)
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='opciones')
    def opciones(self, request: Request) -> Response:
        """Entrega opciones mínimas de usuarios, espacios, locales y edificios para formularios."""
        actor = request.user if request.user and request.user.is_authenticated else None
        return Response(self.service.get_opciones(actor=actor))
