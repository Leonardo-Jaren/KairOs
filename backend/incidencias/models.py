from django.conf import settings
from django.db import models


class Incidencia(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE   = 'pendiente',   'Pendiente'
        EN_REVISION = 'en_revision', 'En revisión'
        RESUELTA    = 'resuelta',    'Resuelta'
        CERRADA     = 'cerrada',     'Cerrada'

    class Prioridad(models.TextChoices):
        BAJA    = 'baja',    'Baja'
        MEDIA   = 'media',   'Media'
        ALTA    = 'alta',    'Alta'
        CRITICA = 'critica', 'Crítica'

    id_reporte = models.AutoField(primary_key=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias',
        db_column='id_usuario_fk',
    )
    espacio = models.ForeignKey(
        'espacios.Espacio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias',
        db_column='id_espacio_fk',
    )
    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias',
        db_column='id_equipo_fk',
    )
    fecha_generado = models.DateTimeField(auto_now_add=True)
    descripcion    = models.TextField()

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    prioridad = models.CharField(
        max_length=20,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )

    tecnico_asignado = models.ForeignKey(
        'usuarios.PerfilTecnico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_asignadas',
        db_column='id_tecnico_asignado_fk',
    )
    fecha_asignacion = models.DateTimeField(null=True, blank=True)

    solucion         = models.TextField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    mantenimiento = models.ForeignKey(
        'mantenimiento.Mantenimiento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias',
        db_column='id_mantenimiento_fk',
    )

    class Meta:
        db_table = 'incidencias'
        indexes = [
            models.Index(fields=['fecha_generado'], name='idx_incidencia_fecha'),
            models.Index(fields=['usuario'],        name='idx_incidencia_usuario'),
            models.Index(fields=['estado'],         name='idx_incidencia_estado'),
        ]

    def __str__(self):
        nombre = self.usuario.nombre if self.usuario else 'Anónimo'
        return f"Inc-{self.id_reporte} | {nombre} | {self.get_estado_display()}"
