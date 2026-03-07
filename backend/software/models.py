from django.db import models


class ProductoSoftware(models.Model):
    """
    Catálogo de productos de software con gestión de licencias.
    Cada registro representa un software con su versión y licenciamiento.
    """

    TIPO_LICENCIA_CHOICES = [
        ('perpetua', 'Perpetua'),
        ('suscripcion', 'Suscripción'),
        ('oem', 'OEM'),
        ('volumen', 'Volumen'),
        ('libre', 'Libre / Open Source'),
    ]

    software = models.CharField(
        max_length=200,
        verbose_name='Nombre del software',
        help_text='Ej: Office, AutoCAD',
    )
    version = models.CharField(
        max_length=50,
        verbose_name='Versión',
        help_text='Ej: 2021, 365',
    )
    descripcion = models.TextField(
        blank=True,
        default='',
        verbose_name='Descripción',
    )
    tipo_licencia = models.CharField(
        max_length=30,
        choices=TIPO_LICENCIA_CHOICES,
        verbose_name='Tipo de licencia',
    )
    licencias_totales = models.IntegerField(
        default=0,
        verbose_name='Licencias totales',
    )
    fecha_expiracion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de expiración',
    )
    costo_anual_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name='Costo anual/total',
    )

    class Meta:
        db_table = 'productos_software'
        verbose_name = 'Producto de Software'
        verbose_name_plural = 'Productos de Software'
        ordering = ['software', 'version']
        constraints = [
            models.UniqueConstraint(
                fields=['software', 'version'],
                name='uq_software_version',
            ),
        ]
        indexes = [
            models.Index(fields=['software'], name='idx_producto_sw_nombre'),
            models.Index(fields=['tipo_licencia'], name='idx_producto_sw_tipo'),
        ]

    def __str__(self):
        return f"{self.software} v{self.version}"

    @property
    def licencias_disponibles(self):
        """Calcula cuántas licencias quedan disponibles."""
        usadas = self.instalaciones.count()
        return self.licencias_totales - usadas


class SoftwareInstalado(models.Model):
    """
    Registro de software instalado en equipos específicos.
    Tabla intermedia entre Equipo y ProductoSoftware.
    """

    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.CASCADE,
        related_name='software_instalado',
        verbose_name='Equipo',
    )
    producto_software = models.ForeignKey(
        ProductoSoftware,
        on_delete=models.CASCADE,
        related_name='instalaciones',
        verbose_name='Producto de software',
    )
    numero_licencia_usado = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Número de licencia usado',
    )
    fecha_instalacion = models.DateField(
        verbose_name='Fecha de instalación',
    )

    class Meta:
        db_table = 'software_instalado'
        verbose_name = 'Software Instalado'
        verbose_name_plural = 'Software Instalados'
        constraints = [
            models.UniqueConstraint(
                fields=['equipo', 'producto_software'],
                name='uq_equipo_software',
            ),
        ]

    def __str__(self):
        return f"{self.producto_software} en {self.equipo.codigo}"
