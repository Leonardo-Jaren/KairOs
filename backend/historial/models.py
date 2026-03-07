from django.db import models


class Historial(models.Model):
    """
    Registro histórico de eventos asociados a equipos.
    Puede estar vinculado a un mantenimiento específico.
    Ej: 'Se asignó a laboratorio LAB-203', 'Se realizó mantenimiento preventivo'.
    """

    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name='Equipo',
    )
    mantenimiento = models.OneToOneField(
        'mantenimiento.Mantenimiento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial',
        verbose_name='Mantenimiento asociado',
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del evento',
    )
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Ej: Se asignó a laboratorio LAB-203',
    )

    class Meta:
        db_table = 'historial'
        verbose_name = 'Historial'
        verbose_name_plural = 'Historiales'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha'], name='idx_historial_fecha'),
            models.Index(fields=['equipo'], name='idx_historial_equipo'),
        ]

    def __str__(self):
        return f"Hist-{self.id} ({self.equipo.codigo}) - {self.fecha:%Y-%m-%d}"
