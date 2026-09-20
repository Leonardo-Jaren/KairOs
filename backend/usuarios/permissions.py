from rest_framework.permissions import BasePermission, SAFE_METHODS

from shared.constants import (
    ROL_SUPERADMIN,
    ROL_ADMIN,
    ROL_RESPONSABLE,
    ROL_TECNICO,
    ROL_DOCENTE,
    ROL_USUARIO,
)


class CanManageDocentes(BasePermission):
    """
    Superadministrador y Administrador: acceso CRUD completo.
    Responsable: gestión de técnicos, docentes y usuarios a su cargo.
    Técnico: puede listar (GET) y crear (POST) solo usuarios con rol docente; sin acceso a permisos ni auditoría de otros.
    Otros: sin acceso.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol in (ROL_SUPERADMIN, ROL_ADMIN, ROL_RESPONSABLE) or request.user.is_superuser:
            return True
        if request.user.rol == ROL_TECNICO:
            # Técnicos solo tienen permiso de lectura (SAFE_METHODS); no pueden crear, editar ni eliminar
            if getattr(view, 'action', None) in ('permisos', 'actividad'):
                return False
            return request.method in SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol in (ROL_SUPERADMIN, ROL_ADMIN) or request.user.is_superuser:
            return True
        if request.user.rol == ROL_RESPONSABLE:
            if request.method in SAFE_METHODS:
                return True
            return obj.id == request.user.id or (
                obj.supervisor_id == request.user.id
                and obj.rol in (ROL_TECNICO, ROL_DOCENTE, ROL_USUARIO)
            )
        if request.user.rol == ROL_TECNICO:
            if getattr(view, 'action', None) in ('permisos', 'actividad'):
                return False
            return request.method in SAFE_METHODS
        return False


