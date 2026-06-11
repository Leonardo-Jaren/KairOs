from django.conf import settings
from django.db import models


class Historial(models.Model):
    """
    Registro de auditoría genérico.

    Esta tabla NO es administrada por Django (managed = False):
    PostgreSQL la crea a partir de bd.sql y la llena automáticamente
    mediante la función audit_trigger() que se dispara en cada
    INSERT / UPDATE / DELETE sobre las tablas auditadas.

    Django únicamente lee este modelo; nunca escribe en él.
    """

    class Accion(models.TextChoices):
        CREAR      = 'crear',      'Crear'
        ACTUALIZAR = 'actualizar', 'Actualizar'
        ELIMINAR   = 'eliminar',   'Eliminar'

    id_historial = models.AutoField(primary_key=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historial_acciones',
        db_column='id_usuario_fk',
    )
    accion         = models.CharField(max_length=20, choices=Accion.choices)
    tabla_afectada = models.CharField(max_length=100)
    registro_id    = models.IntegerField()

    # JSONB en PostgreSQL — row_to_json(OLD) / row_to_json(NEW) del trigger
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos     = models.JSONField(null=True, blank=True)

    # INET en PostgreSQL; Django lo lee como string sin conversión adicional
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    fecha = models.DateTimeField()

    class Meta:
        db_table = 'historial'
        managed  = False  # tabla creada y poblada por PostgreSQL, no por Django

    def __str__(self):
        return f"Hist-{self.id_historial} | {self.tabla_afectada}#{self.registro_id} | {self.accion}"
