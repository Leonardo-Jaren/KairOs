from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from espacios.permissions import CanManageEdificio
from espacios.serializers import CiudadCreateSerializer, CiudadSerializer
from espacios.services import CiudadService
from shared.base import BaseViewSet


class CiudadViewSet(BaseViewSet):
    """Expone la consulta y creación del catálogo territorial de ciudades."""

    service = CiudadService()
    serializer_class = CiudadSerializer
    permission_classes = [CanManageEdificio]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return CiudadCreateSerializer
        return CiudadSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.service.listar(request.query_params.get('search', ''))
        return self.get_collection_response(queryset)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ciudad = self.service.create(serializer.validated_data, actor=request.user)
        return Response(CiudadSerializer(ciudad).data, status=status.HTTP_201_CREATED)
