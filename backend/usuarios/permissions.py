from rest_framework import permissions

class CanManageDocentes(permissions.BasePermission):
    """
    Permisos personalizados para la gestión de usuarios:
    - Administrador: Acceso total (CRUD).
    - Técnico: Solo puede listar (GET) y crear (POST) usuarios con rol 'docente'.
    - Otros roles: Sin acceso.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # El administrador tiene acceso a todos los endpoints del viewset
        if request.user.rol == 'admin':
            return True
            
        # El técnico tiene acceso a listar y crear
        if request.user.rol == 'tecnico':
            if request.method in permissions.SAFE_METHODS or request.method == 'POST':
                return True
                
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # El administrador tiene acceso total a cualquier objeto
        if request.user.rol == 'admin':
            return True
            
        # El técnico solo tiene permisos sobre usuarios que son docentes
        if request.user.rol == 'tecnico':
            return obj.rol == 'docente'
            
        return False
