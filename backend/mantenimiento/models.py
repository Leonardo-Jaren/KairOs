from django.db import models
from shared.models import BaseModel


class Mantenimiento(BaseModel):
    """
    Tickets de mantenimiento para equipos.
    Puede ser preventivo o correctivo, con seguimiento de estado.
    """

    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cancelado', 'Cancelado'),
    ]

    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.CASCADE,
        related_name='mantenimientos',
        verbose_name='Equipo',
    )
    fecha = models.DateField(
        verbose_name='Fecha del ticket',
    )
    tipo_mantenimiento = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de mantenimiento',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado',
    )
    descripcion = models.TextField(
        verbose_name='Descripción del problema',
    )

    class Meta:
        db_table = 'mantenimiento'
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['estado'], name='idx_mant_estado'),
            models.Index(fields=['tipo_mantenimiento'], name='idx_mant_tipo'),
            models.Index(fields=['fecha'], name='idx_mant_fecha'),
        ]

    def __str__(self):
        return f"Mant-{self.id} ({self.equipo.codigo}) - {self.get_estado_display()}"


class TecnicoMantenimiento(BaseModel):
    """
    Tabla intermedia que asigna técnicos a tickets de mantenimiento.
    Un mantenimiento puede tener varios técnicos asignados.
    """

    mantenimiento = models.ForeignKey(
        Mantenimiento,
        on_delete=models.CASCADE,
        related_name='tecnicos_asignados',
        verbose_name='Mantenimiento',
    )
    tecnico = models.ForeignKey(
        'usuarios.PerfilTecnico',
        on_delete=models.CASCADE,
        related_name='mantenimientos_asignados',
        verbose_name='Técnico',
    )

    class Meta:
        db_table = 'tecnico_mantenimiento'
        verbose_name = 'Asignación Técnico - Mantenimiento'
        verbose_name_plural = 'Asignaciones Técnico - Mantenimiento'
        constraints = [
            models.UniqueConstraint(
                fields=['mantenimiento', 'tecnico'],
                name='uq_mantenimiento_tecnico',
            ),
        ]

    def __str__(self):
        return f"{self.tecnico} -> Mant-{self.mantenimiento.id}"
