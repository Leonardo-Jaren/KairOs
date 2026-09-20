from rest_framework.permissions import BasePermission, SAFE_METHODS

from shared.constants import (
    ROL_SUPERADMIN,
    ROL_ADMIN,
    ROL_RESPONSABLE,
    ROL_TECNICO,
)
from shared.permissions import HasModulePermission


class CanManageEspacio(BasePermission):
    """
    Permite acceso evaluando los permisos efectivos del módulo 'espacios'.
    Superadmin tiene acceso total; roles operativos según matriz base o personalizada; otros sin acceso.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == ROL_SUPERADMIN or request.user.is_superuser:
            return True
        accion = HasModulePermission.ACCIONES_MAP.get(request.method, 'ver')
        return request.user.tiene_permiso('espacios', accion)


class CanManageEdificio(BasePermission):
    """
    Permite acceso a edificios/pabellones evaluando permisos del módulo 'espacios'.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == ROL_SUPERADMIN or request.user.is_superuser:
            return True
        accion = HasModulePermission.ACCIONES_MAP.get(request.method, 'ver')
        return request.user.tiene_permiso('espacios', accion)




class CanManageEspacioUsuario(BasePermission):
    """
    Permite escritura a administradores/superadministradores y lectura a responsables y técnicos.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol in (ROL_SUPERADMIN, ROL_ADMIN) or request.user.is_superuser:
            return True
        if getattr(view, 'action', None) == 'opciones':
            return False
        return (
            request.user.rol in (ROL_RESPONSABLE, ROL_TECNICO)
            and request.method in SAFE_METHODS
        )

