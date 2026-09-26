from rest_framework import permissions

from shared.constants import ROL_DOCENTE, ROL_SUPERADMIN, ROL_USUARIO
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
        if request.user.rol in (ROL_DOCENTE, ROL_USUARIO):
            return request.method in ('GET', 'HEAD', 'OPTIONS', 'POST') and (
                request.user.tiene_permiso('incidencias', 'crear' if request.method == 'POST' else 'ver')
            )
        accion = HasModulePermission.ACCIONES_MAP.get(request.method, 'ver')
        return request.user.tiene_permiso('incidencias', accion)

    def has_object_permission(self, request, view, obj):
        if request.user.rol in (ROL_DOCENTE, ROL_USUARIO):
            return request.method in ('GET', 'HEAD', 'OPTIONS') and obj.created_by_id == request.user.id
        return True


