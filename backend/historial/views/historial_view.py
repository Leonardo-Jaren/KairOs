from django.core.exceptions import ObjectDoesNotExist 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from historial.repositories.historial_repository import HistorialRepository
from historial.serializers import HistorialSerializer, HistorialWriteSerializer
from historial.services.historial_service import HistorialService

def get_service():
    """
    Factory function que construye el servicio con su repositorio.
    Centraliza la inyección de dependencias.
    """
    return HistorialService(repository=HistorialRepository())

# ── Lista y Creación ──────────────────────────────────────────────────────────

class HistorialListCreateView(APIView):
    """
    GET  /historial/          → Lista todos los registros.
    POST /historial/          → Crea un nuevo registro.
    """

    def get(self, request):
        try:
            service    = get_service()
            historiales = service.listar_historial()
            serializer = HistorialSerializer(historiales, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        serializer = HistorialWriteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service   = get_service()
            historial = service.crear_historial(serializer.validated_data)
            response  = HistorialSerializer(historial)
            return Response(response.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ── Detalle, Actualización y Eliminación ──────────────────────────────────────

class HistorialDetailView(APIView):
    """
    GET    /historial/<id>/   → Retorna un registro por ID.
    PUT    /historial/<id>/   → Actualización completa.
    PATCH  /historial/<id>/   → Actualización parcial.
    DELETE /historial/<id>/   → Elimina un registro.
    """

    def get(self, request, id_historial: int):
        try:
            service   = get_service()
            historial = service.obtener_historial(id_historial)
            serializer = HistorialSerializer(historial)
            return Response(serializer.data, status=status.HTTP_200_OK)                        

        except ObjectDoesNotExist as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def put(self, request, id_historial: int):
        return self._actualizar(request, id_historial, parcial=False)
    
    def patch(self, request, id_historial: int):
        return self._actualizar(request, id_historial, parcial=True)
    
    def _actualizar(self, request, id_historial: int, parcial: bool):
        serializer = HistorialWriteSerializer(
            data=request.data, 
            partial=parcial
        )  

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            service = get_service()
            historial = service.actualizar_historial(
                id_historial, 
                serializer.validated_data
            )
            response = HistorialSerializer(historial)
            return Response(response.data, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def delete(self, rquest, id_historial: int):
        try:
            service = get_service()
            service.eliminar_historial(id_historial)
            return Response(
                {"mensaje": f"Historial con ID {id_historial} eliminado exitosamente."},
                status=status.HTTP_200_OK
                )

        except ObjectDoesNotExist as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ── Filtros por FK ────────────────────────────────────────────────────────────        

class HistorialPorEquipoView(APIView):
    """
    GET /historial/equipo/<id_equipo>/ → Lista historiales asociados a un equipo.
    """

    def get(self, request, id_equipo: int):
        try:
            service = get_service()
            historiales = service.listar_por_equipo(id_equipo)
            serializer = HistorialSerializer(historiales, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HistorialPorMantenimientoView(APIView):
    """
    GET /historial/mantenimiento/<id_mantenimiento>/
      → Lista historiales asociados a un mantenimiento.
    """

    def get(self, request, id_mantenimiento: int):
        try:
            service = get_service()
            historiales = service.listar_por_mantenimiento(id_mantenimiento)
            serializer = HistorialSerializer(historiales, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        