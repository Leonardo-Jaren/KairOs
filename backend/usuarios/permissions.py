from rest_framework.permissions import BasePermission
from usuarios.models import Usuario


class EsAdmin(BasePermission):
    """Solo usuarios con rol administrador."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.rol == Usuario.Rol.ADMIN
        )


class EsAdminOTecnico(BasePermission):
    """Administradores y técnicos — pueden ver información del sistema."""

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.rol in [Usuario.Rol.ADMIN, Usuario.Rol.TECNICO]
        )


class EsAdminOElMismoPropietario(BasePermission):
    """
    A nivel de objeto: admin puede todo,
    un usuario solo puede modificarse a sí mismo.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.rol == Usuario.Rol.ADMIN or
            obj.id_usuario == request.user.id_usuario
        )
