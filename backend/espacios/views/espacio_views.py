from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from espacios.serializers.espacio_serializers import (
    EspacioReadSerializer,
    EspacioCreateSerializer,
    EspacioUpdateSerializer,
)
from espacios.services.espacio_service import EspacioService
from espacios.repositories.espacio_repository import EspacioRepository
from espacios.exceptions import EspacioNoEncontrado, DatosInvalidos
from usuarios.permissions import EsAdmin


class EspacioViewSet(viewsets.ViewSet):

    def get_service(self):
        return EspacioService(EspacioRepository())

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        return [IsAuthenticated(), EsAdmin()]

    # ----------------------------------------------------------------
    # GET /espacios/?pabellon={id}
    # ----------------------------------------------------------------
    def list(self, request):
        pabellon_id = request.query_params.get("pabellon")
        espacios = self.get_service().listar_espacios(
            pabellon_id=int(pabellon_id) if pabellon_id else None
        )
        serializer = EspacioReadSerializer(espacios, many=True)
        return Response(serializer.data)

    # ----------------------------------------------------------------
    # GET /espacios/{id}/
    # ----------------------------------------------------------------
    def retrieve(self, request, pk=None):
        try:
            espacio = self.get_service().get_espacio(pk)
            return Response(EspacioReadSerializer(espacio).data)

        except EspacioNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------
    # POST /espacios/
    # ----------------------------------------------------------------
    def create(self, request):
        serializer = EspacioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            espacio = self.get_service().crear_espacio(serializer.validated_data)
            return Response(
                EspacioReadSerializer(espacio).data,
                status=status.HTTP_201_CREATED,
            )
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # PATCH /espacios/{id}/
    # ----------------------------------------------------------------
    def partial_update(self, request, pk=None):
        serializer = EspacioUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            espacio = self.get_service().actualizar_espacio(pk, serializer.validated_data)
            return Response(EspacioReadSerializer(espacio).data)

        except EspacioNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # DELETE /espacios/{id}/
    # ----------------------------------------------------------------
    def destroy(self, request, pk=None):
        try:
            self.get_service().eliminar_espacio(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except EspacioNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
