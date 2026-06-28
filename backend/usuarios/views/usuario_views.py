from shared.base_viewset import BaseViewSet
from usuarios.services import UsuarioService
from usuarios.serializers import UsuarioSerializer, UsuarioCreateUpdateSerializer


class UsuarioViewSet(BaseViewSet):
    """
    Controlador API (ViewSet) para la gestión completa (CRUD) de la entidad Usuario.
    Hereda de BaseViewSet para automatizar y estandarizar las operaciones básicas,
    al mismo tiempo que inyecta UsuarioService respetando SOLID.
    """
    service = UsuarioService()
    serializer_class = UsuarioSerializer

    def get_serializer_class(self):
        """
        Retorna dinámicamente el serializador apropiado:
        - UsuarioCreateUpdateSerializer para acciones de escritura (crear, actualizar).
        - UsuarioSerializer para acciones de lectura (listar, recuperar).
        """
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioCreateUpdateSerializer
        return self.serializer_class
