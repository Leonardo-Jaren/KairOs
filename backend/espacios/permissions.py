from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS

from shared.constants import (
    ROL_SUPERADMIN,
    ROL_ADMIN,
    ROL_RESPONSABLE,
    ROL_TECNICO,
    ROL_DOCENTE,
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
    Controla el acceso a la gestión de asignaciones territoriales (EspacioUsuario):
    - Superadmin y Admin tienen acceso global total de lectura y escritura.
    - Responsable de Sede tiene acceso a lectura y al endpoint catálogo 'opciones'.
    - Responsable de Sede puede crear, editar o eliminar asignaciones ÚNICAMENTE
      en las sedes físicas activas que tiene asignadas en UsuarioSede.
      Si intenta operar en una sede ajena, se deniega con HTTP 403 (PermissionDenied).
    - Técnico y Docente tienen acceso de solo lectura (SAFE_METHODS), bloqueados en 'opciones'.
    - Otros roles no tienen acceso.
    """

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        # 1. Acceso irrestricto para superadmin y administradores
        if request.user.rol in (ROL_SUPERADMIN, ROL_ADMIN) or request.user.is_superuser:
            return True

        # 2. Catálogo de opciones de formulario: permitido para admin y responsable
        if getattr(view, 'action', None) == 'opciones':
            return request.user.rol == ROL_RESPONSABLE

        # 3. Métodos seguros de lectura: responsable, técnico y docente
        if request.method in SAFE_METHODS:
            return request.user.rol in (ROL_RESPONSABLE, ROL_TECNICO, ROL_DOCENTE)

        # 4. Operaciones de escritura (POST, PUT, PATCH, DELETE)
        if request.user.rol != ROL_RESPONSABLE:
            return False

        # 5. Validación de sedes activas para el rol responsable
        sedes_activas = set(
            request.user.usuario_sedes.filter(activo=True).values_list('local_id', flat=True)
        )
        if not sedes_activas:
            raise PermissionDenied('No tienes sedes asignadas para gestionar asignaciones.')

        target_local_id = self._resolver_local_id(request, view)
        if target_local_id is not None and target_local_id not in sedes_activas:
            raise PermissionDenied('No tienes autorización para gestionar asignaciones en una sede ajena.')

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        """Valida permisos a nivel de instancia para PUT, PATCH, DELETE y GET individual."""
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.rol in (ROL_SUPERADMIN, ROL_ADMIN) or request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return request.user.rol in (ROL_RESPONSABLE, ROL_TECNICO, ROL_DOCENTE)

        if request.user.rol != ROL_RESPONSABLE:
            return False

        sedes_activas = set(
            request.user.usuario_sedes.filter(activo=True).values_list('local_id', flat=True)
        )
        target_local_id = self._resolver_local_id(request, view, obj=obj)
        if target_local_id is not None and target_local_id not in sedes_activas:
            raise PermissionDenied('No tienes autorización para gestionar asignaciones en una sede ajena.')

        return True

    def _resolver_local_id(self, request, view, obj=None) -> int | None:
        """
        Determina el local_id involucrado a partir del objeto, payload o identificador URL.
        """
        # 1. Desde el objeto en BD si está disponible
        if obj is not None:
            if getattr(obj, 'local_id', None):
                return obj.local_id
            if getattr(obj, 'edificio_id', None) and obj.edificio:
                return obj.edificio.local_id
            if getattr(obj, 'espacio_id', None) and obj.espacio and obj.espacio.edificio:
                return obj.espacio.edificio.local_id
            return None

        # 2. Desde el cuerpo de la solicitud (request.data)
        data = getattr(request, 'data', {})
        if isinstance(data, dict):
            local_id = data.get('local_id')
            if local_id:
                try:
                    return int(local_id)
                except (ValueError, TypeError):
                    return None

            edificio_id = data.get('edificio_id')
            if edificio_id:
                try:
                    from espacios.models import Edificio
                    return Edificio.objects.filter(id=int(edificio_id)).values_list('local_id', flat=True).first()
                except (ValueError, TypeError):
                    return None

            espacio_id = data.get('espacio_id')
            if espacio_id:
                try:
                    from espacios.models import Espacio
                    return Espacio.objects.filter(id=int(espacio_id)).values_list('edificio__local_id', flat=True).first()
                except (ValueError, TypeError):
                    return None

        # 3. Desde la clave primaria en la URL (pk) para PUT, PATCH o DELETE
        pk = view.kwargs.get('pk') if hasattr(view, 'kwargs') and view.kwargs else None
        if pk:
            try:
                from espacios.models import EspacioUsuario
                asig = EspacioUsuario.objects.filter(id=pk).select_related('edificio', 'espacio__edificio').first()
                if asig:
                    return (
                        asig.local_id
                        or (asig.edificio.local_id if asig.edificio else None)
                        or (asig.espacio.edificio.local_id if asig.espacio and asig.espacio.edificio else None)
                    )
            except (ValueError, TypeError):
                return None

        return None
