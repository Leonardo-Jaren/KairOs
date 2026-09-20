from rest_framework import permissions

from shared.constants import ROL_SUPERADMIN
from shared.permissions import HasModulePermission


class CanManageIncidencia(permissions.BasePermission):
    """
    Permite acceso evaluando los permisos efectivos del modulo 'incidencias'.
    Superadmin tiene acceso total; roles operativos segun matriz base o personalizada.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == ROL_SUPERADMIN or request.user.is_superuser:
            return True
        accion = HasModulePermission.ACCIONES_MAP.get(request.method, 'ver')
        return request.user.tiene_permiso('incidencias', accion)


