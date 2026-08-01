from shared.base_viewset import BaseViewSet
from usuarios.services import UsuarioService
from usuarios.serializers import UsuarioSerializer, UsuarioCreateUpdateSerializer
from usuarios.permissions import CanManageDocentes
from rest_framework.response import Response


class UsuarioViewSet(BaseViewSet):
    """
    Controlador API (ViewSet) para la gestión completa (CRUD) de la entidad Usuario.
    Hereda de BaseViewSet para automatizar y estandarizar las operaciones básicas,
    al mismo tiempo que inyecta UsuarioService respetando SOLID.
    """
    service = UsuarioService()
    serializer_class = UsuarioSerializer
    permission_classes = [CanManageDocentes]

    def get_serializer_class(self):
        """
        Retorna dinámicamente el serializador apropiado:
        - UsuarioCreateUpdateSerializer para acciones de escritura (crear, actualizar).
        - UsuarioSerializer para acciones de lectura (listar, recuperar).
        """
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioCreateUpdateSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs) -> Response:
        """
        Sobrescribe list para asegurar que si es técnico, solo vea docentes.
        """
        queryset = self.service.get_all()
        
        # Filtro de seguridad adicional para técnicos
        if request.user and request.user.rol == 'tecnico':
            queryset = queryset.filter(rol='docente')
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
