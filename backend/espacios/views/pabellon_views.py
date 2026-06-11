from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from espacios.serializers.pabellon_serializers import (
    PabellonReadSerializer,
    PabellonCreateSerializer,
    PabellonUpdateSerializer,
)
from espacios.services.pabellon_service import PabellonService
from espacios.repositories.pabellon_repository import PabellonRepository
from espacios.exceptions import PabellonNoEncontrado, DatosInvalidos
from usuarios.permissions import EsAdmin, EsAdminOTecnico


class PabellonViewSet(viewsets.ViewSet):

    def get_service(self):
        return PabellonService(PabellonRepository())

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        return [IsAuthenticated(), EsAdmin()]

    # ----------------------------------------------------------------
    # GET /pabellones/
    # ----------------------------------------------------------------
    def list(self, request):
        pabellones = self.get_service().listar_pabellones()
        serializer = PabellonReadSerializer(pabellones, many=True)
        return Response(serializer.data)

    # ----------------------------------------------------------------
    # GET /pabellones/{id}/
    # ----------------------------------------------------------------
    def retrieve(self, request, pk=None):
        try:
            pabellon = self.get_service().get_pabellon(pk)
            return Response(PabellonReadSerializer(pabellon).data)

        except PabellonNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------
    # POST /pabellones/
    # ----------------------------------------------------------------
    def create(self, request):
        serializer = PabellonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pabellon = self.get_service().crear_pabellon(serializer.validated_data)
            return Response(
                PabellonReadSerializer(pabellon).data,
                status=status.HTTP_201_CREATED,
            )
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # PATCH /pabellones/{id}/
    # ----------------------------------------------------------------
    def partial_update(self, request, pk=None):
        serializer = PabellonUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pabellon = self.get_service().actualizar_pabellon(pk, serializer.validated_data)
            return Response(PabellonReadSerializer(pabellon).data)

        except PabellonNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # DELETE /pabellones/{id}/
    # ----------------------------------------------------------------
    def destroy(self, request, pk=None):
        try:
            self.get_service().eliminar_pabellon(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except PabellonNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
