from django.db import models


class Pabellon(models.Model):
    id_pabellon = models.AutoField(primary_key=True)
    nombre      = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(null=True, blank=True, verbose_name='Descripción')
    total_pisos = models.IntegerField(default=1, verbose_name='Total de pisos')

    class Meta:
        db_table        = 'pabellones'
        verbose_name    = 'Pabellón'
        verbose_name_plural = 'Pabellones'

    def __str__(self):
        return self.nombre


class Espacio(models.Model):
    id_espacio     = models.AutoField(primary_key=True)
    codigo_espacio = models.CharField(max_length=50, unique=True, verbose_name='Código')
    pabellon       = models.ForeignKey(
        Pabellon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='espacios',
        db_column='id_pabellon_fk',
        verbose_name='Pabellón',
    )
    piso        = models.CharField(max_length=20, null=True, blank=True, verbose_name='Piso')
    tipo        = models.CharField(max_length=50, null=True, blank=True, verbose_name='Tipo')
    capacidad   = models.IntegerField(null=True, blank=True, verbose_name='Capacidad')
    descripcion = models.TextField(null=True, blank=True, verbose_name='Descripción')

    class Meta:
        db_table        = 'espacios'
        verbose_name    = 'Espacio'
        verbose_name_plural = 'Espacios'
        indexes = [
            models.Index(fields=['pabellon'], name='idx_espacio_pabellon'),
        ]

    def __str__(self):
        return f"{self.codigo_espacio} ({self.tipo or 'Sin tipo'})"
