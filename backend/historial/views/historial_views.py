from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from historial.serializers.historial_serializers import HistorialReadSerializer
from historial.services.historial_service import HistorialService
from historial.repositories.historial_repository import HistorialRepository
from historial.exceptions import RegistroNoEncontrado
from usuarios.permissions import EsAdmin


class HistorialViewSet(viewsets.ViewSet):
    """
    ViewSet de sólo lectura — no registra list_route de escritura.

    SRP  — coordina HTTP ↔ servicio; el servicio coordina con el repositorio.
    ISP  — el ViewSet no implementa create/update/destroy porque no existen
           en la capa de servicio; exponerlos sería mentirle al cliente.
    """

    def get_service(self) -> HistorialService:
        return HistorialService(HistorialRepository())

    def get_permissions(self):
        return [IsAuthenticated(), EsAdmin()]

    # ------------------------------------------------------------------ #
    # GET /historial/
    # Filtros (query params):
    #   tabla=       — nombre de la tabla auditada (ej. 'equipos')
    #   registro_id= — ID del registro dentro de esa tabla
    #   usuario=     — id_usuario del responsable de la acción
    #   accion=      — crear | actualizar | eliminar
    #   fecha_desde= — YYYY-MM-DD
    #   fecha_hasta= — YYYY-MM-DD
    # ------------------------------------------------------------------ #
    def list(self, request):
        p = request.query_params

        tabla       = p.get('tabla')
        registro_q  = p.get('registro_id')
        usuario_q   = p.get('usuario')
        accion      = p.get('accion')
        fecha_desde = p.get('fecha_desde')
        fecha_hasta = p.get('fecha_hasta')

        registros = self.get_service().listar_historial(
            tabla=tabla,
            registro_id=int(registro_q) if registro_q else None,
            usuario_id=int(usuario_q)   if usuario_q  else None,
            accion=accion,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        return Response(HistorialReadSerializer(registros, many=True).data)

    # ------------------------------------------------------------------ #
    # GET /historial/{id}/
    # ------------------------------------------------------------------ #
    def retrieve(self, request, pk=None):
        try:
            registro = self.get_service().get_registro(pk)
            return Response(HistorialReadSerializer(registro).data)
        except RegistroNoEncontrado as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
