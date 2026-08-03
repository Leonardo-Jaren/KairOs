from rest_framework import permissions


class CanManageMantenimiento(permissions.BasePermission):
    """
    Permisos de la gestion de mantenimiento:
    - Administrador: acceso total (CRUD).
    - Tecnico: puede listar, crear y actualizar tickets, pero no eliminarlos.
    - Otros roles: sin acceso.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.rol == 'admin':
            return True

        if request.user.rol == 'tecnico':
            return request.method != 'DELETE'

        return False
