from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from incidencias.serializers.incidencia_serializers import (
    IncidenciaReadSerializer,
    IncidenciaCreateSerializer,
    AsignarTecnicoSerializer,
    ResolverIncidenciaSerializer,
    VincularMantenimientoSerializer,
)
from incidencias.services.incidencia_service import IncidenciaService
from incidencias.repositories.incidencia_repository import IncidenciaRepository
from incidencias.exceptions import (
    IncidenciaNoEncontrada,
    TecnicoNoEncontrado,
    MantenimientoNoEncontrado,
    DatosInvalidos,
)
from usuarios.models import Usuario
from usuarios.permissions import EsAdmin, EsAdminOTecnico


class IncidenciaViewSet(viewsets.ViewSet):
    """
    SRP  — coordina HTTP ↔ servicio; la lógica vive en IncidenciaService.
    DIP  — depende de abstracciones inyectadas en get_service().
    ISP  — cada @action declara sólo los permisos que necesita.
    """

    def get_service(self) -> IncidenciaService:
        return IncidenciaService(IncidenciaRepository())

    def get_permissions(self):
        # Cualquier usuario autenticado puede reportar o consultar
        if self.action in ['list', 'retrieve', 'create']:
            return [IsAuthenticated()]
        # Resolver lo puede un técnico o admin
        if self.action == 'resolver':
            return [IsAuthenticated(), EsAdminOTecnico()]
        # Asignar, cerrar y vincular mantenimiento sólo admin
        return [IsAuthenticated(), EsAdmin()]

    # ------------------------------------------------------------------ #
    # GET /incidencias/
    # Admin/Técnico ven todas; usuario normal sólo las suyas.
    # Filtros: ?estado= &espacio= &usuario=
    # ------------------------------------------------------------------ #
    def list(self, request):
        usuario    = request.user
        estado_q   = request.query_params.get('estado')
        espacio_q  = request.query_params.get('espacio')
        usuario_q  = request.query_params.get('usuario')

        if usuario.rol == Usuario.Rol.USUARIO:
            # usuario normal: sólo sus propias incidencias
            incidencias = self.get_service().listar_incidencias(
                usuario_id=usuario.id_usuario
            )
        else:
            incidencias = self.get_service().listar_incidencias(
                usuario_id=int(usuario_q)  if usuario_q  else None,
                espacio_id=int(espacio_q)  if espacio_q  else None,
                estado=estado_q            if estado_q   else None,
            )

        return Response(IncidenciaReadSerializer(incidencias, many=True).data)

    # ------------------------------------------------------------------ #
    # GET /incidencias/{id}/
    # ------------------------------------------------------------------ #
    def retrieve(self, request, pk=None):
        try:
            incidencia = self.get_service().get_incidencia(pk)
            # usuario normal sólo puede ver las suyas
            if (
                request.user.rol == Usuario.Rol.USUARIO
                and incidencia.usuario_id != request.user.id_usuario
            ):
                return Response(
                    {'detail': 'No tiene permiso para ver esta incidencia'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(IncidenciaReadSerializer(incidencia).data)
        except IncidenciaNoEncontrada as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------ #
    # POST /incidencias/
    # ------------------------------------------------------------------ #
    def create(self, request):
        serializer = IncidenciaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            incidencia = self.get_service().crear_incidencia(
                serializer.validated_data,
                request.user,
            )
            return Response(
                IncidenciaReadSerializer(incidencia).data,
                status=status.HTTP_201_CREATED,
            )
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # DELETE /incidencias/{id}/  (sólo admin)
    # ------------------------------------------------------------------ #
    def destroy(self, request, pk=None):
        service = self.get_service()
        try:
            incidencia = service.get_incidencia(pk)
            service.repo.delete(incidencia)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except IncidenciaNoEncontrada as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------ #
    # POST /incidencias/{id}/asignar/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=['post'], url_path='asignar')
    def asignar(self, request, pk=None):
        serializer = AsignarTecnicoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            incidencia = self.get_service().asignar_tecnico(
                pk,
                serializer.validated_data['id_tecnico'],
            )
            return Response(IncidenciaReadSerializer(incidencia).data)
        except IncidenciaNoEncontrada as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except TecnicoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # POST /incidencias/{id}/resolver/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=['post'], url_path='resolver')
    def resolver(self, request, pk=None):
        serializer = ResolverIncidenciaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            incidencia = self.get_service().resolver_incidencia(
                pk,
                serializer.validated_data['solucion'],
            )
            return Response(IncidenciaReadSerializer(incidencia).data)
        except IncidenciaNoEncontrada as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # POST /incidencias/{id}/cerrar/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=['post'], url_path='cerrar')
    def cerrar(self, request, pk=None):
        try:
            incidencia = self.get_service().cerrar_incidencia(pk)
            return Response(IncidenciaReadSerializer(incidencia).data)
        except IncidenciaNoEncontrada as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # POST /incidencias/{id}/mantenimiento/
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=['post'], url_path='mantenimiento')
    def vincular_mantenimiento(self, request, pk=None):
        serializer = VincularMantenimientoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            incidencia = self.get_service().vincular_mantenimiento(
                pk,
                serializer.validated_data['id_mantenimiento'],
            )
            return Response(IncidenciaReadSerializer(incidencia).data)
        except IncidenciaNoEncontrada as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except MantenimientoNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
