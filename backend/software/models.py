from django.db import models
from django.utils import timezone


class ProductoSoftware(models.Model):

    id_producto_software = models.AutoField(primary_key=True)

    software          = models.CharField(max_length=255, verbose_name='Software')
    version           = models.CharField(max_length=50, null=True, blank=True, verbose_name='Versión')
    descripcion       = models.TextField(null=True, blank=True, verbose_name='Descripción')
    tipo_licencia     = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tipo de licencia')
    licencias_totales = models.IntegerField(default=0, verbose_name='Licencias totales')
    fecha_expiracion  = models.DateField(null=True, blank=True, verbose_name='Fecha de expiración')
    costo_anual_total = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name='Costo anual total',
    )

    class Meta:
        db_table = 'productos_software'
        verbose_name = 'Producto de Software'
        verbose_name_plural = 'Productos de Software'
        constraints = [
            models.UniqueConstraint(
                fields=['software', 'version'],
                name='uq_software_version',
            ),
        ]

    def __str__(self):
        return f"{self.software} v{self.version or 'N/A'}"

    @property
    def licencias_usadas(self) -> int:
        return self.instalaciones.count()

    @property
    def licencias_disponibles(self) -> int:
        return self.licencias_totales - self.licencias_usadas

    @property
    def licencia_vencida(self) -> bool:
        if self.fecha_expiracion is None:
            return False
        return self.fecha_expiracion < timezone.now().date()


class SoftwareInstalado(models.Model):

    id_instalacion = models.AutoField(primary_key=True)

    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.CASCADE,
        related_name='software_instalado',
        db_column='id_equipo_fk',
        verbose_name='Equipo',
    )
    producto_software = models.ForeignKey(
        ProductoSoftware,
        on_delete=models.CASCADE,
        related_name='instalaciones',
        db_column='id_producto_software_fk',
        verbose_name='Producto de software',
    )
    numero_licencia_usado = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Número de licencia usado',
    )
    fecha_instalacion = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de instalación',
    )

    class Meta:
        db_table = 'software_instalado'
        verbose_name = 'Software Instalado'
        verbose_name_plural = 'Software Instalado'
        constraints = [
            models.UniqueConstraint(
                fields=['equipo', 'producto_software'],
                name='uq_equipo_software',
            ),
        ]

    def __str__(self):
        return f"{self.producto_software} → {self.equipo.codigo}"
