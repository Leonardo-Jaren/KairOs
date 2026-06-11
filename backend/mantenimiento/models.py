from django.db import models
from django.conf import settings
from django.utils import timezone


class Mantenimiento(models.Model):

    class TipoMantenimiento(models.TextChoices):
        PREVENTIVO = 'Preventivo', 'Preventivo'
        CORRECTIVO = 'Correctivo', 'Correctivo'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        RESUELTO  = 'resuelto',  'Resuelto'

    id_mantenimiento = models.AutoField(primary_key=True)

    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.CASCADE,
        related_name='mantenimientos',
        db_column='id_equipo_fk',
    )
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_cierre = models.DateField(null=True, blank=True)
    tipo_mantenimiento = models.CharField(
        max_length=50,
        choices=TipoMantenimiento.choices,
        null=True,
        blank=True,
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    descripcion          = models.TextField(null=True, blank=True)
    observaciones_cierre = models.TextField(null=True, blank=True)
    usuario_cierre = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos_cerrados',
        db_column='id_usuario_cierre_fk',
    )

    class Meta:
        db_table = 'mantenimiento'
        indexes = [
            models.Index(fields=['estado'],             name='idx_mant_estado'),
            models.Index(fields=['tipo_mantenimiento'], name='idx_mant_tipo'),
            models.Index(fields=['fecha_inicio'],       name='idx_mant_fecha'),
        ]

    def __str__(self):
        return f"Mant-{self.id_mantenimiento} ({self.equipo.codigo}) - {self.get_estado_display()}"


class TecnicoMantenimiento(models.Model):

    id = models.AutoField(primary_key=True)

    mantenimiento = models.ForeignKey(
        Mantenimiento,
        on_delete=models.CASCADE,
        related_name='tecnicos_asignados',
        db_column='id_mantenimiento_fk',
    )
    tecnico = models.ForeignKey(
        'usuarios.PerfilTecnico',
        on_delete=models.CASCADE,
        related_name='mantenimientos_asignados',
        db_column='id_tecnico_fk',
    )

    class Meta:
        db_table = 'tecnico_mantenimiento'
        constraints = [
            models.UniqueConstraint(
                fields=['mantenimiento', 'tecnico'],
                name='uq_mantenimiento_tecnico',
            ),
        ]

    def __str__(self):
        return f"Tecnico {self.tecnico_id} -> Mant-{self.mantenimiento_id}"
