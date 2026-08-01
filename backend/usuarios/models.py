from django.contrib.auth.models import AbstractUser
from django.db import models
from shared.models import BaseModel


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Se usa correo electrónico como identificador principal de autenticación.
    """

    ROL_CHOICES = [
        ('usuario', 'Usuario'), #clase base que heredan los demás 
        ('admin', 'Administrador'),
        ('tecnico', 'Técnico'),
        ('docente', 'Docente'), #Se esta añadiendo para poder dividir el como se interactua con los reportes
    ]

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
        ]

    def __str__(self):
        return f"{self.nombre} ({self.correo})"


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
