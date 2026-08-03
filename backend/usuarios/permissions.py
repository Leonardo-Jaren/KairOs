from rest_framework.permissions import BasePermission, SAFE_METHODS

from shared.constants import ROL_ADMIN, ROL_TECNICO, ROL_DOCENTE


class CanManageDocentes(BasePermission):
    """
    Administrador: acceso CRUD completo.
    Técnico: puede listar (GET) y crear (POST) solo usuarios con rol docente.
    Otros: sin acceso.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == ROL_ADMIN:
            return True
        if request.user.rol == ROL_TECNICO:
            return request.method in SAFE_METHODS or request.method == 'POST'
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.rol == ROL_ADMIN:
            return True
        if request.user.rol == ROL_TECNICO:
            return obj.rol == ROL_DOCENTE
        return False
