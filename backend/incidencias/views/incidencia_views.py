from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from incidencias.permissions import CanManageIncidencia
from incidencias.serializers import IncidenciaCreateUpdateSerializer, IncidenciaSerializer
from incidencias.services import IncidenciaService
from shared.base import BaseViewSet


class IncidenciaViewSet(BaseViewSet):
    """Expone el CRUD y consulta operativa de incidencias."""

    service = IncidenciaService()
    serializer_class = IncidenciaSerializer
    permission_classes = [CanManageIncidencia]

    def get_serializer_class(self):
        """Selecciona serializers separados para lectura y escritura."""
        if self.action in ['create', 'update', 'partial_update']:
            return IncidenciaCreateUpdateSerializer
        return IncidenciaSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista incidencias aplicando busqueda, espacio, equipo, tipo y estado.

        Un docente solo ve las incidencias que el mismo registro.
        """
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            espacio_id=self.parse_integer_query(request.query_params.get('espacio_id')),
            equipo_id=self.parse_integer_query(request.query_params.get('equipo_id')),
            tipo_incidencia=request.query_params.get('tipo_incidencia', ''),
            estado=request.query_params.get('estado', ''),
            actor=request.user,
        )
        return self.get_collection_response(queryset)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Obtiene el detalle de una incidencia visible para el usuario actual."""
        instance = self.service.get_visible_by_id(kwargs['pk'], actor=request.user)
        return Response(self.get_serializer(instance).data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Reporta una incidencia validando datos de negocio."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.service.create(serializer.validated_data, actor=request.user)
        return Response(IncidenciaSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Actualiza total o parcialmente una incidencia existente."""
        partial = kwargs.pop('partial', False)
        instance = self.service.get_by_id(kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update(kwargs['pk'], serializer.validated_data, actor=request.user)
        return Response(IncidenciaSerializer(updated).data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Elimina logicamente una incidencia."""
        self.service.delete(kwargs['pk'], actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request: Request) -> Response:
        """Entrega indicadores agregados del modulo de incidencias."""
        return Response(self.service.get_estadisticas(actor=request.user))

    @action(detail=False, methods=['get'], url_path='espacios-opciones')
    def espacios_opciones(self, request: Request) -> Response:
        """Entrega espacios vigentes para el formulario de incidencias.

        Expuesto aqui (y no en /api/v1/espacios/) porque un docente puede
        reportar incidencias pero no tiene acceso de lectura al modulo de
        espacios.
        """
        return Response(self.service.get_espacios_opciones())

    @action(detail=False, methods=['get'], url_path='equipos-opciones')
    def equipos_opciones(self, request: Request) -> Response:
        """Entrega equipos vigentes para el formulario de incidencias.

        Expuesto aqui (y no en /api/v1/equipos/) por la misma razon que
        espacios_opciones: un docente no tiene acceso de lectura al modulo
        de equipos.
        """
        return Response(self.service.get_equipos_opciones(
            espacio_id=self.parse_integer_query(request.query_params.get('espacio_id'))
        ))
