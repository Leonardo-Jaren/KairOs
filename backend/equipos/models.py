from django.db import models
from common.models import BaseModel


class Equipo(BaseModel):
    """
    Equipos informáticos registrados en el sistema.
    Cada equipo pertenece a un espacio físico y tiene un estado operativo.
    """

    TIPO_EQUIPO_CHOICES = [
        ('desktop', 'Desktop'),
        ('laptop', 'Laptop'),
        ('servidor', 'Servidor'),
        ('impresora', 'Impresora'),
        ('proyector', 'Proyector'),
        ('monitor', 'Monitor'),
        ('otro', 'Otro'),
    ]

    MODO_ADQUISICION_CHOICES = [
        ('comprado', 'Comprado'),
        ('arrendado', 'Arrendado'),
        ('donado', 'Donado'),
    ]

    ESTADO_CHOICES = [
        ('en_uso', 'En uso'),
        ('en_mantenimiento', 'En mantenimiento'),
        ('dañado', 'Dañado'),
        ('de_baja', 'De baja'),
    ]

    espacio = models.ForeignKey(
        'espacios.Espacio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipos',
        verbose_name='Espacio asignado',
    )
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código interno',
        help_text='Identificador interno del equipo',
    )
    numero_serie = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Número de serie',
        help_text='Número de serie del fabricante',
    )
    numero_mac = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Dirección MAC',
        help_text='Ej: MAC:10001:10F',
    )
    tipo_equipo = models.CharField(
        max_length=30,
        choices=TIPO_EQUIPO_CHOICES,
        verbose_name='Tipo de equipo',
    )
    marca = models.CharField(
        max_length=100,
        verbose_name='Marca',
    )
    modelo = models.CharField(
        max_length=100,
        verbose_name='Modelo',
    )
    modo_adquisicion = models.CharField(
        max_length=20,
        choices=MODO_ADQUISICION_CHOICES,
        verbose_name='Modo de adquisición',
    )
    fecha_adquisicion = models.DateField(
        verbose_name='Fecha de adquisición',
    )
    fecha_renovacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de renovación',
        help_text='Solo si aplica (equipos arrendados)',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='en_uso',
        verbose_name='Estado',
    )
    responsable_usuario = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Usuario asignado/responsable',
    )

    class Meta:
        db_table = 'equipos'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['codigo'], name='idx_equipo_codigo'),
            models.Index(fields=['numero_serie'], name='idx_equipo_serie'),
            models.Index(fields=['estado'], name='idx_equipo_estado'),
            models.Index(fields=['tipo_equipo'], name='idx_equipo_tipo'),
            models.Index(fields=['numero_mac'], name='idx_equipo_mac'),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.marca} {self.modelo} ({self.get_estado_display()})"


class Componente(BaseModel):
    """
    Componentes internos de un equipo.
    Ej: CPU, RAM, SSD, GPU, etc.
    """

    TIPO_CHOICES = [
        ('cpu', 'CPU'),
        ('ram', 'RAM'),
        ('ssd', 'SSD'),
        ('hdd', 'HDD'),
        ('gpu', 'GPU'),
        ('motherboard', 'Motherboard'),
        ('fuente', 'Fuente de Poder'),
        ('nic', 'Tarjeta de Red'),
        ('otro', 'Otro'),
    ]

    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='componentes',
        verbose_name='Equipo',
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de componente',
        help_text='Ej: CPU, RAM, SSD',
    )
    modelo = models.CharField(
        max_length=100,
        verbose_name='Modelo',
        help_text='Ej: Fury, Ryzen 5 5600X',
    )
    descripcion = models.TextField(
        blank=True,
        default='',
        verbose_name='Descripción/Detalle',
        help_text='Ej: 16GB DDR4 3200MHz',
    )

    class Meta:
        db_table = 'componentes'
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.modelo} ({self.equipo.codigo})"
