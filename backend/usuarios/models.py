from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Se usa correo electrónico como identificador principal de autenticación.
    """

    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('tecnico', 'Técnico'),
        ('usuario', 'Usuario'),
    ]

    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre completo',
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Usar correo como campo de autenticación
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['username', 'nombre']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['correo'], name='idx_usuario_correo'),
            models.Index(fields=['rol'], name='idx_usuario_rol'),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.correo})"


class PerfilTecnico(models.Model):
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
