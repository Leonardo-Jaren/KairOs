from django.db import models
from django.conf import settings


class Equipo(models.Model):

    class Estado(models.TextChoices):
        NO_USADO         = 'no usado',         'No usado'
        EN_USO           = 'en uso',           'En uso'
        EN_MANTENIMIENTO = 'en mantenimiento', 'En mantenimiento'
        DAÑADO           = 'dañado',           'Dañado'

    id_equipo = models.AutoField(primary_key=True)

    espacio = models.ForeignKey(
        'espacios.Espacio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipos',
        db_column='id_espacio_fk',
        verbose_name='Espacio',
    )
    codigo = models.CharField(max_length=100, unique=True, verbose_name='Código')
    numero_serie = models.CharField(max_length=100, null=True, blank=True, verbose_name='Número de serie')
    numero_mac   = models.CharField(max_length=100, null=True, blank=True, verbose_name='Dirección MAC')
    tipo_equipo  = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Tipo de equipo')
    marca        = models.CharField(max_length=100, null=True, blank=True, verbose_name='Marca')
    modelo       = models.CharField(max_length=100, null=True, blank=True, verbose_name='Modelo')
    modo_adquisicion  = models.CharField(max_length=100, null=True, blank=True, verbose_name='Modo de adquisición')
    fecha_adquisicion = models.DateField(null=True, blank=True, verbose_name='Fecha de adquisición')
    fecha_renovacion  = models.DateField(null=True, blank=True, verbose_name='Fecha de renovación')

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.NO_USADO,
        verbose_name='Estado',
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipos_a_cargo',
        db_column='id_responsable_fk',
        verbose_name='Responsable',
    )

    class Meta:
        db_table = 'equipos'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        indexes = [
            models.Index(fields=['codigo'], name='idx_equipo_codigo'),
        ]

    def __str__(self):
        return f"{self.codigo} — {self.marca or ''} {self.modelo or ''}".strip()


class Componente(models.Model):

    id_componente = models.AutoField(primary_key=True)

    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='componentes',
        db_column='id_equipo_fk',
        verbose_name='Equipo',
    )
    tipo         = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Tipo')
    modelo       = models.CharField(max_length=50,  null=True, blank=True, verbose_name='Modelo')
    numero_serie = models.CharField(max_length=100, null=True, blank=True, verbose_name='Número de serie')
    descripcion  = models.TextField(null=True, blank=True, verbose_name='Descripción')

    class Meta:
        db_table = 'componentes'
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'

    def __str__(self):
        return f"{self.tipo or 'Componente'} — {self.modelo or ''} ({self.equipo.codigo})"
