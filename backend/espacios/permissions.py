from rest_framework.permissions import BasePermission, SAFE_METHODS

from shared.constants import ROL_ADMIN, ROL_TECNICO
from shared.permissions import IsAdminOrTecnicoReadOnly


class CanManageEspacio(IsAdminOrTecnicoReadOnly):
    """Permite CRUD a administradores y lectura a técnicos."""


class CanManageEspacioUsuario(BasePermission):
    """Permite escritura a administradores y lectura a técnicos. Bloquea opciones para técnicos."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == ROL_ADMIN:
            return True
        if getattr(view, 'action', None) == 'opciones':
            return False
        return request.user.rol == ROL_TECNICO and request.method in SAFE_METHODS
