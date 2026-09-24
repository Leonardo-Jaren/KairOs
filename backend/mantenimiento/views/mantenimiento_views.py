from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from mantenimiento.permissions import CanManageMantenimiento
from mantenimiento.serializers import (
    MantenimientoCreateUpdateSerializer,
    MantenimientoFinalizeSerializer,
    MantenimientoSerializer,
)
from mantenimiento.services import MantenimientoService
from shared.base import BaseViewSet


class MantenimientoViewSet(BaseViewSet):
    """Expone la gestion de tickets de mantenimiento de equipos."""

    service = MantenimientoService()
    serializer_class = MantenimientoSerializer
    permission_classes = [CanManageMantenimiento]

    def get_serializer_class(self):
        """Selecciona serializers separados para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return MantenimientoCreateUpdateSerializer
        return MantenimientoSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista tickets aplicando busqueda, estado, tipo y equipo."""
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            estado=request.query_params.get('estado', ''),
            tipo_mantenimiento=request.query_params.get('tipo_mantenimiento', ''),
            equipo_id=self.parse_integer_query(request.query_params.get('equipo_id')),
            actor=request.user,
        )
        return self.get_collection_response(queryset)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Obtiene un ticket de mantenimiento por identificador."""
        instance = self.service.get_visible_by_id(kwargs['pk'], actor=request.user)
        return Response(MantenimientoSerializer(instance).data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Crea un ticket de mantenimiento junto a sus tecnicos asignados."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data, actor=request.user)
        return Response(MantenimientoSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza total o parcialmente un ticket existente."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_visible_by_id(kwargs['pk'], actor=request.user)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(kwargs['pk'], serializer.validated_data, actor=request.user)
        return Response(MantenimientoSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Elimina logicamente un ticket de mantenimiento."""
        self.service.get_visible_by_id(kwargs['pk'], actor=request.user)
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def iniciar(self, request: Request, pk=None) -> Response:
        """Pasa una orden pendiente a atencion."""
        instance = self.service.iniciar(pk, actor=request.user)
        return Response(MantenimientoSerializer(instance).data)

    @action(detail=True, methods=['post'])
    def finalizar(self, request: Request, pk=None) -> Response:
        """Finaliza una orden y aplica su resultado operativo."""
        serializer = MantenimientoFinalizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.finalizar(
            pk,
            serializer.validated_data,
            actor=request.user,
        )
        incidencia = result['incidencia']
        mantenimiento = result['mantenimiento']
        equipo = result['equipo']
        incidencia_data = None
        if incidencia is not None:
            from incidencias.serializers import IncidenciaSerializer

            incidencia_data = IncidenciaSerializer(incidencia).data
            incidencia_data['cerrada_automaticamente'] = result['cerrada_automaticamente']
        return Response({
            'mantenimiento': MantenimientoSerializer(mantenimiento).data,
            'equipo': {
                'id': equipo.id,
                'estado': equipo.estado,
                'estado_display': equipo.get_estado_display(),
            },
            'incidencia': incidencia_data,
            'siguiente_accion': result['siguiente_accion'],
        })

    @action(detail=False, methods=['get'])
    def estadisticas(self, request: Request) -> Response:
        """Entrega indicadores agregados para la cabecera del modulo."""
        return Response(self.service.get_estadisticas(actor=request.user))

    @action(detail=False, methods=['get'], url_path='tecnicos-disponibles')
    def tecnicos_disponibles(self, request: Request) -> Response:
        """Entrega los tecnicos vigentes disponibles para asignar."""
        return Response(self.service.get_tecnicos_disponibles())
