from django.conf import settings
from django.db import models
from shared.models import BaseModel


class Incidencia(BaseModel):
    """
    Reportes de incidencias generados por usuarios.
    Asociados obligatoriamente a un espacio y opcionalmente a un equipo.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incidencias',
        verbose_name='Usuario que reporta',
    )
    espacio = models.ForeignKey(
        'espacios.Espacio',
        on_delete=models.CASCADE,
        related_name='incidencias',
        verbose_name='Ubicación',
        help_text='Espacio donde ocurrió la incidencia (obligatorio)',
    )
    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias',
        verbose_name='Equipo afectado',
    )
    fecha_generado = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de generación',
    )
    descripcion = models.TextField(
        verbose_name='Descripción de la incidencia',
    )

    class Meta:
        db_table = 'incidencias'
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
        ordering = ['-fecha_generado']
        indexes = [
            models.Index(fields=['fecha_generado'], name='idx_incidencia_fecha'),
            models.Index(fields=['usuario'], name='idx_incidencia_usuario'),
        ]

    def __str__(self):
        return f"Inc-{self.id} por {self.usuario.nombre} ({self.fecha_generado:%Y-%m-%d})"
