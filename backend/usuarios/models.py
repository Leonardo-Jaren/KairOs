from django.contrib.auth.models import AbstractUser
from django.db import models
from shared.constants import (
    ROLES,
    ROL_SUPERADMIN,
    ROL_PERMISOS_BASE,
    MODULOS_SISTEMA,
    ACCIONES_SISTEMA,
)
from shared.models import BaseModel


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Se usa correo electrónico como identificador principal de autenticación.
    """

    ROL_CHOICES = ROLES

    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre completo',
    )
    apellido = models.CharField(
        max_length=255,
        verbose_name='Apellido completo',
        default='',
    )
    dni = models.CharField(
        max_length=8,
        unique=True,
        verbose_name='DNI',
        null=True,
        blank=True,
    )
    correo = models.EmailField(
        unique=True,
        verbose_name='Correo electrónico',
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='usuario',
        verbose_name='Rol',
    )
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinados',
        verbose_name='Supervisor directo',
    )
    sedes = models.ManyToManyField(
        'espacios.Local',
        through='UsuarioSede',
        through_fields=('usuario', 'local'),
        related_name='usuarios',
        blank=True,
        verbose_name='Sedes asignadas',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Usar correo como campo de autenticación
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['username', 'nombre']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['correo'], name='idx_usuario_correo'),
            models.Index(fields=['rol'], name='idx_usuario_rol'),
            models.Index(fields=['supervisor'], name='idx_usuario_supervisor'),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    def tiene_permiso(self, modulo: str, accion: str) -> bool:
        """Verifica si el usuario tiene permiso efectivo sobre un módulo y acción."""
        if self.rol == ROL_SUPERADMIN or self.is_superuser:
            return True

        if hasattr(self, '_prefetched_objects_cache') and 'permisos_personalizados' in self._prefetched_objects_cache:
            for p in self.permisos_personalizados.all():
                if p.modulo == modulo and p.accion == accion:
                    return p.permitido
        else:
            custom = self.permisos_personalizados.filter(modulo=modulo, accion=accion).first()
            if custom is not None:
                return custom.permitido

        base = ROL_PERMISOS_BASE.get(self.rol, {}).get(modulo, {})
        return base.get(accion, False)

    def get_permisos_efectivos(self) -> dict:
        """Devuelve un mapa anidado modulo -> accion -> bool con los permisos finales calculados."""
        permisos = {}
        base_rol = ROL_PERMISOS_BASE.get(self.rol, {})
        modulos = [m[0] for m in MODULOS_SISTEMA]

        for mod in modulos:
            permisos[mod] = {}
            for acc in ACCIONES_SISTEMA:
                if self.rol == ROL_SUPERADMIN or self.is_superuser:
                    permisos[mod][acc] = True
                else:
                    permisos[mod][acc] = base_rol.get(mod, {}).get(acc, False)

        if self.rol != ROL_SUPERADMIN and not self.is_superuser:
            custom_permisos = self.permisos_personalizados.all()
            for custom in custom_permisos:
                if custom.modulo in permisos and custom.accion in permisos[custom.modulo]:
                    permisos[custom.modulo][custom.accion] = custom.permitido

        return permisos


class PerfilTecnico(BaseModel):
    """
    Perfil específico para usuarios con rol de técnico.
    Relación 1:1 con Usuario.
    """

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_tecnico',
        verbose_name='Usuario',
    )
    area = models.CharField(
        max_length=100,
        verbose_name='Área',
        help_text='Ej: Cedeco',
    )

    class Meta:
        db_table = 'perfil_tecnico'
        verbose_name = 'Perfil Técnico'
        verbose_name_plural = 'Perfiles Técnicos'

    def __str__(self):
        return f"Técnico: {self.usuario.nombre} - {self.area}"


class UsuarioSede(BaseModel):
    """
    Relación Many-to-Many entre un Usuario y una Sede física (espacios.Local).
    """

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='usuario_sedes',
        verbose_name='Usuario',
    )
    local = models.ForeignKey(
        'espacios.Local',
        on_delete=models.CASCADE,
        related_name='usuario_sedes',
        verbose_name='Local / Sede',
    )
    es_sede_principal = models.BooleanField(
        default=False,
        verbose_name='¿Es sede principal?',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Asignación activa',
    )

    class Meta:
        db_table = 'usuario_sedes'
        verbose_name = 'Asignación de Sede'
        verbose_name_plural = 'Asignaciones de Sedes'
        unique_together = ('usuario', 'local')
        ordering = ['-es_sede_principal', 'local__nombre']

    def __str__(self):
        return f"{self.usuario.username} -> {self.local.nombre}"


class PermisoPersonalizado(BaseModel):
    """
    Permiso individual por módulo y acción que sobreescribe la plantilla por defecto del rol.
    """

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='permisos_personalizados',
        verbose_name='Usuario',
    )
    modulo = models.CharField(
        max_length=50,
        choices=MODULOS_SISTEMA,
        verbose_name='Módulo',
    )
    accion = models.CharField(
        max_length=20,
        choices=[(a, a.capitalize()) for a in ACCIONES_SISTEMA],
        verbose_name='Acción',
    )
    permitido = models.BooleanField(
        default=True,
        verbose_name='Permitido',
    )

    class Meta:
        db_table = 'permisos_personalizados'
        verbose_name = 'Permiso Personalizado'
        verbose_name_plural = 'Permisos Personalizados'
        unique_together = ('usuario', 'modulo', 'accion')
        ordering = ['modulo', 'accion']

    def __str__(self):
        estado = "Permitido" if self.permitido else "Denegado"
        return f"{self.usuario.username} - {self.modulo}.{self.accion} ({estado})"

