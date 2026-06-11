from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from equipos.serializers.equipo_serializers import (
    EquipoReadSerializer,
    EquipoCreateSerializer,
    EquipoUpdateSerializer,
)
from equipos.services.equipo_service import EquipoService
from equipos.repositories.equipo_repository import EquipoRepository
from equipos.exceptions import EquipoNoEncontrado, DatosInvalidos
from usuarios.permissions import EsAdmin, EsAdminOTecnico


class EquipoViewSet(viewsets.ViewSet):

    def get_service(self):
        return EquipoService(EquipoRepository())

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), EsAdminOTecnico()]

        if self.action == "cambiar_estado":
            return [IsAuthenticated(), EsAdminOTecnico()]

        return [IsAuthenticated(), EsAdmin()]

    # ----------------------------------------------------------------
    # GET /equipos/?estado=&espacio=
    # ----------------------------------------------------------------
    def list(self, request):
        estado     = request.query_params.get("estado")
        espacio_id = request.query_params.get("espacio")
        equipos = self.get_service().listar_equipos(
            estado=estado,
            espacio_id=int(espacio_id) if espacio_id else None,
        )
        return Response(EquipoReadSerializer(equipos, many=True).data)

    # ----------------------------------------------------------------
    # GET /equipos/{id}/
    # ----------------------------------------------------------------
    def retrieve(self, request, pk=None):
        try:
            equipo = self.get_service().get_equipo(pk)
            return Response(EquipoReadSerializer(equipo).data)
        except EquipoNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------
    # POST /equipos/
    # ----------------------------------------------------------------
    def create(self, request):
        serializer = EquipoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            equipo = self.get_service().crear_equipo(serializer.validated_data)
            return Response(EquipoReadSerializer(equipo).data, status=status.HTTP_201_CREATED)
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # PATCH /equipos/{id}/
    # ----------------------------------------------------------------
    def partial_update(self, request, pk=None):
        serializer = EquipoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            equipo = self.get_service().actualizar_equipo(pk, serializer.validated_data)
            return Response(EquipoReadSerializer(equipo).data)
        except EquipoNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # DELETE /equipos/{id}/
    # ----------------------------------------------------------------
    def destroy(self, request, pk=None):
        try:
            self.get_service().eliminar_equipo(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except EquipoNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------
    # PATCH /equipos/{id}/estado/
    # ----------------------------------------------------------------
    @action(detail=True, methods=["patch"], url_path="estado")
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint dedicado para cambiar solo el estado del equipo.
        SRP: separado del partial_update general para que el frontend
        no tenga que enviar todos los campos para un cambio de estado.
        """
        estado = request.data.get("estado")
        if not estado:
            return Response({"detail": "El campo 'estado' es requerido."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            equipo = self.get_service().cambiar_estado(pk, estado)
            return Response(EquipoReadSerializer(equipo).data)
        except EquipoNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
