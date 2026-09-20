from rest_framework.permissions import BasePermission, SAFE_METHODS

from shared.constants import ROL_SUPERADMIN, ROL_ADMIN, ROL_TECNICO


class IsAdminOrTecnicoReadOnly(BasePermission):
    """Superadmin y Admin: CRUD completo. Técnico: solo lectura (GET/HEAD/OPTIONS). Otros: sin acceso."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol in (ROL_SUPERADMIN, ROL_ADMIN):
            return True
        return request.user.rol == ROL_TECNICO and request.method in SAFE_METHODS


class HasModulePermission(BasePermission):
    """
    Verifica si el usuario autenticado tiene permiso para el módulo y acción requeridos.
    """

    ACCIONES_MAP = {
        'GET': 'ver',
        'HEAD': 'ver',
        'OPTIONS': 'ver',
        'POST': 'crear',
        'PUT': 'editar',
        'PATCH': 'editar',
        'DELETE': 'eliminar',
    }

    def __init__(self, modulo: str | None = None, accion: str | None = None):
        self.modulo = modulo
        self.accion = accion

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.rol == ROL_SUPERADMIN or request.user.is_superuser:
            return True

        modulo = self.modulo or getattr(view, 'modulo', None)
        accion = self.accion or self.ACCIONES_MAP.get(request.method, 'ver')

        if not modulo:
            return True

        return request.user.tiene_permiso(modulo, accion)

