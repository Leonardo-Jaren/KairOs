from django.conf import settings
from django.db import models
from shared.models import BaseModel


class Espacio(BaseModel):
    """
    Espacios físicos: laboratorios, oficinas, aulas, etc.
    Ejemplo de codigo_espacio: LAB-203
    """

    TIPO_CHOICES = [
        ('laboratorio', 'Laboratorio'),
        ('oficina', 'Oficina'),
        ('aula', 'Aula'),
        ('sala_computo', 'Sala de Cómputo'),
        ('otro', 'Otro'),
    ]

    codigo_espacio = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código del espacio',
        help_text='Ej: LAB-203',
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de espacio',
    )
    pabellon = models.CharField(
        max_length=100,
        verbose_name='Pabellón',
        help_text='Ej: Pabellón 1',
    )
    piso = models.CharField(
        max_length=20,
        verbose_name='Piso',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Espacio activo',
    )

    class Meta:
        db_table = 'espacios'
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['codigo_espacio']
        indexes = [
            models.Index(fields=['codigo_espacio'], name='idx_espacio_codigo'),
            models.Index(fields=['tipo'], name='idx_espacio_tipo'),
            models.Index(fields=['pabellon'], name='idx_espacio_pabellon'),
        ]

    def __str__(self):
        return f"{self.codigo_espacio} - {self.get_tipo_display()} ({self.pabellon})"


class EspacioUsuario(BaseModel):
    """Relaciona usuarios con los espacios donde tienen responsabilidad."""

    TIPO_RESPONSABILIDAD_CHOICES = [
        ('responsable', 'Responsable'),
        ('tecnico', 'Soporte técnico'),
        ('docente', 'Docente asignado'),
    ]

    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.CASCADE,
        related_name='asignaciones_usuario',
        verbose_name='Espacio',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones_espacio',
        verbose_name='Usuario',
    )
    tipo_responsabilidad = models.CharField(
        max_length=20,
        choices=TIPO_RESPONSABILIDAD_CHOICES,
        default='responsable',
        verbose_name='Tipo de responsabilidad',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Asignación activa',
    )

    class Meta:
        db_table = 'espacios_usuarios'
        verbose_name = 'Asignación de usuario a espacio'
        verbose_name_plural = 'Asignaciones de usuarios a espacios'
        ordering = ['espacio__codigo_espacio', 'usuario__nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['espacio', 'usuario'],
                name='uniq_espacio_usuario',
            ),
        ]
        indexes = [
            models.Index(fields=['espacio', 'activo'], name='idx_asig_esp_activa'),
            models.Index(fields=['usuario', 'activo'], name='idx_asig_usr_activa'),
        ]

    def __str__(self):
        return f'{self.usuario} - {self.espacio.codigo_espacio}'
