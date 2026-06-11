from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mantenimiento.serializers.mantenimiento_serializers import (
    MantenimientoReadSerializer,
    MantenimientoCreateSerializer,
    MantenimientoUpdateSerializer,
    MantenimientoCerrarSerializer,
    AsignarTecnicoSerializer,
)
from mantenimiento.services.mantenimiento_service import MantenimientoService
from mantenimiento.repositories.mantenimiento_repository import MantenimientoRepository
from mantenimiento.repositories.tecnico_mantenimiento_repository import TecnicoMantenimientoRepository
from mantenimiento.exceptions import MantenimientoNoEncontrado, TecnicoNoEncontrado, DatosInvalidos
from usuarios.permissions import EsAdmin, EsAdminOTecnico


class MantenimientoViewSet(viewsets.ViewSet):
    """
    SRP  — sólo coordina HTTP ↔ servicio; toda lógica vive en MantenimientoService.
    DIP  — recibe el servicio construido en get_service(), fácil de reemplazar en tests.
    """

    def get_service(self) -> MantenimientoService:
        return MantenimientoService(
            MantenimientoRepository(),
            TecnicoMantenimientoRepository(),
        )

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), EsAdminOTecnico()]
        return [IsAuthenticated(), EsAdmin()]

    # ------------------------------------------------------------------ #
    # GET /mantenimiento/?equipo=&pendientes=true
    # ------------------------------------------------------------------ #
    def list(self, request):
        equipo_id       = request.query_params.get('equipo')
        solo_pendientes = request.query_params.get('pendientes') == 'true'
        mantenimientos  = self.get_service().listar_mantenimientos(
            equipo_id=int(equipo_id) if equipo_id else None,
            solo_pendientes=solo_pendientes,
        )
        return Response(MantenimientoReadSerializer(mantenimientos, many=True).data)

    # ------------------------------------------------------------------ #
    # GET /mantenimiento/{id}/
    # ------------------------------------------------------------------ #
    def retrieve(self, request, pk=None):
        try:
            mant = self.get_service().get_mantenimiento(pk)
            return Response(MantenimientoReadSerializer(mant).data)
        except MantenimientoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------ #
    # POST /mantenimiento/
    # ------------------------------------------------------------------ #
    def create(self, request):
        serializer = MantenimientoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            mant = self.get_service().crear_mantenimiento(serializer.validated_data)
            return Response(
                MantenimientoReadSerializer(mant).data,
                status=status.HTTP_201_CREATED,
            )
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # PATCH /mantenimiento/{id}/
    # ------------------------------------------------------------------ #
    def partial_update(self, request, pk=None):
        serializer = MantenimientoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            mant = self.get_service().actualizar_mantenimiento(pk, serializer.validated_data)
            return Response(MantenimientoReadSerializer(mant).data)
        except MantenimientoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # DELETE /mantenimiento/{id}/
    # ------------------------------------------------------------------ #
    def destroy(self, request, pk=None):
        service = self.get_service()
        try:
            mant = service.get_mantenimiento(pk)
            service.repo.delete(mant)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MantenimientoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------ #
    # POST /mantenimiento/{id}/cerrar/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=['post'], url_path='cerrar')
    def cerrar(self, request, pk=None):
        serializer = MantenimientoCerrarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            mant = self.get_service().cerrar_mantenimiento(
                pk,
                serializer.validated_data,
                request.user,
            )
            return Response(MantenimientoReadSerializer(mant).data)
        except MantenimientoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # POST /mantenimiento/{id}/tecnicos/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=['post'], url_path='tecnicos')
    def asignar_tecnico(self, request, pk=None):
        serializer = AsignarTecnicoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            asignacion = self.get_service().asignar_tecnico(
                pk,
                serializer.validated_data['id_tecnico'],
            )
            return Response(
                {'detail': 'Técnico asignado correctamente', 'id': asignacion.id},
                status=status.HTTP_201_CREATED,
            )
        except MantenimientoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except TecnicoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # DELETE /mantenimiento/{id}/tecnicos/{tecnico_id}/
    # ------------------------------------------------------------------ #
    @action(
        detail=True,
        methods=['delete'],
        url_path=r'tecnicos/(?P<tecnico_id>[^/.]+)',
    )
    def remover_tecnico(self, request, pk=None, tecnico_id=None):
        try:
            self.get_service().remover_tecnico(pk, int(tecnico_id))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MantenimientoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
