from rest_framework import permissions

from shared.constants import ROL_ADMIN, ROL_DOCENTE, ROL_TECNICO


class CanManageIncidencia(permissions.BasePermission):
    """Admin y tecnico: CRUD completo. Docente: solo lectura y creacion."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol in (ROL_ADMIN, ROL_TECNICO):
            return True
        return (
            request.user.rol == ROL_DOCENTE
            and (request.method in permissions.SAFE_METHODS or request.method == 'POST')
        )
