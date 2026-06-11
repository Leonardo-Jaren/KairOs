from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from software.serializers.instalacion_serializers import (
    InstalacionReadSerializer,
    InstalacionCreateSerializer,
)
from software.services.instalacion_service import InstalacionService
from software.repositories.instalacion_repository import InstalacionRepository
from software.repositories.producto_repository import ProductoSoftwareRepository
from software.exceptions import InstalacionNoEncontrada, DatosInvalidos, ProductoSoftwareNoEncontrado
from usuarios.permissions import EsAdmin, EsAdminOTecnico


class InstalacionViewSet(viewsets.ViewSet):

    def get_service(self):
        return InstalacionService(InstalacionRepository(), ProductoSoftwareRepository())

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), EsAdminOTecnico()]
        return [IsAuthenticated(), EsAdmin()]

    # ----------------------------------------------------------------
    # GET /software/instalaciones/?equipo=&producto=
    # ----------------------------------------------------------------
    def list(self, request):
        equipo_id   = request.query_params.get("equipo")
        producto_id = request.query_params.get("producto")
        instalaciones = self.get_service().listar_instalaciones(
            equipo_id=int(equipo_id)   if equipo_id   else None,
            producto_id=int(producto_id) if producto_id else None,
        )
        return Response(InstalacionReadSerializer(instalaciones, many=True).data)

    # ----------------------------------------------------------------
    # POST /software/instalaciones/
    # ----------------------------------------------------------------
    def create(self, request):
        serializer = InstalacionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instalacion = self.get_service().instalar_software(serializer.validated_data)
            return Response(InstalacionReadSerializer(instalacion).data, status=status.HTTP_201_CREATED)
        except (DatosInvalidos, ProductoSoftwareNoEncontrado) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # DELETE /software/instalaciones/{id}/
    # ----------------------------------------------------------------
    def destroy(self, request, pk=None):
        try:
            self.get_service().desinstalar_software(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InstalacionNoEncontrada as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
