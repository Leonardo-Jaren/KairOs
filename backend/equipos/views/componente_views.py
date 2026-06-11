from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from equipos.serializers.componente_serializers import (
    ComponenteReadSerializer,
    ComponenteCreateSerializer,
    ComponenteUpdateSerializer,
)
from equipos.services.componente_service import ComponenteService
from equipos.repositories.componente_repository import ComponenteRepository
from equipos.repositories.equipo_repository import EquipoRepository
from equipos.exceptions import ComponenteNoEncontrado, EquipoNoEncontrado
from usuarios.permissions import EsAdmin, EsAdminOTecnico


class ComponenteViewSet(viewsets.ViewSet):

    def get_service(self):
        return ComponenteService(ComponenteRepository(), EquipoRepository())

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), EsAdminOTecnico()]
        return [IsAuthenticated(), EsAdmin()]

    # ----------------------------------------------------------------
    # GET /equipos/componentes/?equipo={id}
    # ----------------------------------------------------------------
    def list(self, request):
        equipo_id = request.query_params.get("equipo")
        if not equipo_id:
            return Response(
                {"detail": "El parámetro 'equipo' es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            componentes = self.get_service().listar_componentes(int(equipo_id))
            return Response(ComponenteReadSerializer(componentes, many=True).data)
        except EquipoNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------
    # POST /equipos/componentes/
    # ----------------------------------------------------------------
    def create(self, request):
        serializer = ComponenteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        componente = self.get_service().crear_componente(serializer.validated_data)
        return Response(ComponenteReadSerializer(componente).data, status=status.HTTP_201_CREATED)

    # ----------------------------------------------------------------
    # PATCH /equipos/componentes/{id}/
    # ----------------------------------------------------------------
    def partial_update(self, request, pk=None):
        serializer = ComponenteUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            componente = self.get_service().actualizar_componente(pk, serializer.validated_data)
            return Response(ComponenteReadSerializer(componente).data)
        except ComponenteNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------
    # DELETE /equipos/componentes/{id}/
    # ----------------------------------------------------------------
    def destroy(self, request, pk=None):
        try:
            self.get_service().eliminar_componente(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ComponenteNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
