from rest_framework.permissions import BasePermission, SAFE_METHODS

from shared.constants import ROL_ADMIN, ROL_TECNICO


class IsAdminOrTecnicoReadOnly(BasePermission):
    """Admin: CRUD completo. Técnico: solo lectura (GET/HEAD/OPTIONS). Otros: sin acceso."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == ROL_ADMIN:
            return True
        return request.user.rol == ROL_TECNICO and request.method in SAFE_METHODS
