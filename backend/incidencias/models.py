from django.db import models
from shared.models import BaseModel


class Incidencia(BaseModel):
    """
    Reportes de incidencias de hardware o software sobre un equipo,
    con seguimiento de estado hasta su resolución.
    """

    TIPO_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
    ]

    espacio = models.ForeignKey(
        'espacios.Espacio',
        on_delete=models.CASCADE,
        related_name='incidencias',
        verbose_name='Ubicación',
        help_text='Espacio donde ocurrió la incidencia',
    )
    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.CASCADE,
        related_name='incidencias',
        verbose_name='Equipo afectado',
    )
    tipo_incidencia = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de incidencia',
    )
    descripcion = models.TextField(
        verbose_name='Descripción de la incidencia',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado',
    )
    fecha_resolucion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de resolución',
    )

    class Meta:
        db_table = 'incidencias'
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['estado'], name='idx_incidencia_estado'),
            models.Index(fields=['tipo_incidencia'], name='idx_incidencia_tipo'),
            models.Index(fields=['espacio'], name='idx_incidencia_espacio'),
            models.Index(fields=['equipo'], name='idx_incidencia_equipo'),
        ]

    def __str__(self):
        return f"Inc-{self.id} - {self.equipo.codigo} ({self.get_estado_display()})"
