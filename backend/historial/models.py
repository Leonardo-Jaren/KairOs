from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Historial(models.Model):
    """
    Log de auditoría global e inmutable del sistema.
    Registra eventos de cualquier módulo mediante ContentTypes.
    Los eventos se crean exclusivamente desde los servicios — nunca desde la API.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_generados',
        verbose_name='Usuario',
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del evento',
    )
    tipo_evento = models.CharField(
        max_length=100,
        verbose_name='Tipo de evento',
        help_text='Formato modulo.accion — ej. equipo.cambio_estado',
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='Tipo de objeto',
    )
    object_id = models.PositiveIntegerField(
        verbose_name='ID del objeto',
    )
    objeto = GenericForeignKey('content_type', 'object_id')
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Texto legible para mostrar en interfaz.',
    )
    datos_extra = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos adicionales',
        help_text='Estado anterior, nuevo valor, IDs relacionados, etc.',
    )

    class Meta:
        db_table = 'historial'
        verbose_name = 'Evento de auditoría'
        verbose_name_plural = 'Historial de auditoría'
        ordering = ['-fecha']
        indexes = [
            models.Index(
                fields=['content_type', 'object_id', 'fecha'],
                name='idx_historial_objeto_fecha',
            ),
            models.Index(fields=['fecha'], name='idx_historial_fecha'),
            models.Index(fields=['usuario'], name='idx_historial_usuario'),
            models.Index(fields=['tipo_evento'], name='idx_historial_tipo'),
        ]

    def __str__(self):
        return f"[{self.tipo_evento}] {self.content_type} #{self.object_id} — {self.fecha:%Y-%m-%d %H:%M}"
