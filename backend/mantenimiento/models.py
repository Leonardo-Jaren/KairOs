from django.conf import settings
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

    RESULTADO_EQUIPO_CHOICES = [
        ('en_uso', 'En uso'),
        ('en_mantenimiento', 'En mantenimiento'),
        ('dañado', 'Dañado'),
        ('de_baja', 'De baja'),
    ]

    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.CASCADE,
        related_name='mantenimientos',
        verbose_name='Equipo',
    )
    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_reportados',
        verbose_name='Reportado por',
    )
    incidencia_origen = models.ForeignKey(
        'incidencias.Incidencia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos',
        verbose_name='Incidencia de origen',
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
    diagnostico = models.TextField(
        blank=True,
        default='',
        verbose_name='Diagnóstico',
    )
    trabajo_realizado = models.TextField(
        blank=True,
        default='',
        verbose_name='Trabajo realizado',
    )
    resultado_equipo = models.CharField(
        max_length=20,
        choices=RESULTADO_EQUIPO_CHOICES,
        null=True,
        blank=True,
        verbose_name='Resultado del equipo',
    )
    prueba_realizada = models.BooleanField(
        default=False,
        verbose_name='Prueba de funcionamiento realizada',
    )
    observacion_prueba = models.TextField(
        blank=True,
        default='',
        verbose_name='Observación de la prueba',
    )
    verificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_verificados',
        verbose_name='Verificado por',
    )
    fecha_verificacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de verificación',
    )
    fecha_inicio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Inicio de atención',
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fin de atención',
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
            models.Index(fields=['incidencia_origen'], name='idx_mant_incidencia'),
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
