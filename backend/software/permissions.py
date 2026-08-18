from rest_framework.permissions import BasePermission

from shared.constants import ROL_ADMIN, ROL_TECNICO


class CanManageSoftware(BasePermission):
    """Permite consultar y gestionar instalaciones a administradores y tecnicos."""

    def has_permission(self, request, view):
        """Comprueba autenticacion y pertenencia a un rol operativo."""
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol in {ROL_ADMIN, ROL_TECNICO}
        )
