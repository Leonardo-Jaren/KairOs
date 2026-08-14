from rest_framework.request import Request
from rest_framework.response import Response

from shared.base import BaseViewSet
from software.permissions import CanManageSoftware
from software.serializers import ProductoSoftwareSerializer
from software.services import ProductoSoftwareService


class ProductoSoftwareViewSet(BaseViewSet):
    """Expone el catalogo de software a los roles operativos."""

    service = ProductoSoftwareService()
    serializer_class = ProductoSoftwareSerializer
    permission_classes = [CanManageSoftware]
    http_method_names = ['get', 'head', 'options']

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Lista productos aplicando busqueda y tipo de licencia."""
        queryset = self.service.listar(
            busqueda=request.query_params.get('search', ''),
            tipo_licencia=request.query_params.get('tipo_licencia', ''),
        )
        return self.get_collection_response(queryset)
