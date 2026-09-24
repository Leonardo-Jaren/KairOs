from rest_framework import permissions

from shared.constants import (
    ROL_SUPERADMIN,
    ROL_ADMIN,
    ROL_RESPONSABLE,
    ROL_TECNICO,
)
from shared.permissions import HasModulePermission


class CanManageMantenimiento(permissions.BasePermission):
    """
    Permisos de la gestion de mantenimiento evaluando permisos efectivos del modulo 'mantenimiento'.
    Superadministrador tiene acceso total; roles operativos segun matriz base o personalizada.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.rol == ROL_SUPERADMIN or request.user.is_superuser:
            return True

        # Iniciar y finalizar son transiciones operativas de una orden
        # existente; requieren editar, no el permiso de crear órdenes nuevas.
        accion = (
            'editar'
            if getattr(view, 'action', None) in {'iniciar', 'finalizar'}
            else HasModulePermission.ACCIONES_MAP.get(request.method, 'ver')
        )
        return request.user.tiene_permiso('mantenimiento', accion)


