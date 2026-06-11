from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.serializers.user_serializers import (
    UsuarioReadSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
)
from usuarios.services.user_management_service import UserManagementService
from usuarios.repositories.user_repository import UserRepository
from usuarios.exceptions import UsuarioNoEncontrado, DatosInvalidos
from usuarios.permissions import EsAdmin, EsAdminOTecnico, EsAdminOElMismoPropietario


class UsuarioViewSet(viewsets.ViewSet):
    """
    ViewSet manual — no hereda de ModelViewSet para mantener
    el control total sobre cada acción y que pase por el service.
    """

    def get_service(self):
        return UserManagementService(UserRepository())

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), EsAdminOTecnico()]

        if self.action == "create":
            return [IsAuthenticated(), EsAdmin()]

        if self.action == "partial_update":
            return [IsAuthenticated(), EsAdminOElMismoPropietario()]

        if self.action == "destroy":
            return [IsAuthenticated(), EsAdmin()]

        return [IsAuthenticated()]

    # ----------------------------------------------------------------
    # GET /usuarios/
    # ----------------------------------------------------------------
    def list(self, request):
        usuarios = self.get_service().list_usuarios()
        serializer = UsuarioReadSerializer(usuarios, many=True)
        return Response(serializer.data)

    # ----------------------------------------------------------------
    # GET /usuarios/{id}/
    # ----------------------------------------------------------------
    def retrieve(self, request, pk=None):
        try:
            usuario = self.get_service().get_usuario(pk)
            return Response(UsuarioReadSerializer(usuario).data)

        except UsuarioNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------
    # POST /usuarios/
    # ----------------------------------------------------------------
    def create(self, request):
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            usuario = self.get_service().create_usuario(serializer.validated_data)
            return Response(
                UsuarioReadSerializer(usuario).data,
                status=status.HTTP_201_CREATED,
            )
        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # PATCH /usuarios/{id}/
    # ----------------------------------------------------------------
    def partial_update(self, request, pk=None):
        try:
            usuario = self.get_service().get_usuario(pk)
        except UsuarioNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, usuario)

        serializer = UsuarioUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            actualizado = self.get_service().update_usuario(pk, serializer.validated_data)
            return Response(UsuarioReadSerializer(actualizado).data)

        except DatosInvalidos as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # DELETE /usuarios/{id}/  → soft delete
    # ----------------------------------------------------------------
    def destroy(self, request, pk=None):
        try:
            self.get_service().deactivate_usuario(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except UsuarioNoEncontrado as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
