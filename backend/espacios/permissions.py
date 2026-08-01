from rest_framework import permissions


class CanManageEspacio(permissions.BasePermission):
    """Permite CRUD a administradores y lectura a técnicos."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == 'admin':
            return True
        return (
            request.user.rol == 'tecnico'
            and request.method in permissions.SAFE_METHODS
        )


class CanManageEspacioUsuario(permissions.BasePermission):
    """Permite escritura a administradores y lectura a técnicos."""

    def has_permission(self, request, view):
        """Evalúa el rol y el método HTTP solicitado."""
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == 'admin':
            return True
        if getattr(view, 'action', None) == 'opciones':
            return False
        return (
            request.user.rol == 'tecnico'
            and request.method in permissions.SAFE_METHODS
        )
