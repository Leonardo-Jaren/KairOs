from rest_framework import permissions


class CanManageEquipo(permissions.BasePermission):
    """Permite CRUD a administradores y lectura a tecnicos."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == 'admin':
            return True
        return (
            request.user.rol == 'tecnico'
            and request.method in permissions.SAFE_METHODS
        )
