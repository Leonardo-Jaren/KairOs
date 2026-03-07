from django.db import models


class Espacio(models.Model):
    """
    Espacios físicos: laboratorios, oficinas, aulas, etc.
    Ejemplo de codigo_espacio: LAB-203
    """

    TIPO_CHOICES = [
        ('laboratorio', 'Laboratorio'),
        ('oficina', 'Oficina'),
        ('aula', 'Aula'),
        ('sala_computo', 'Sala de Cómputo'),
        ('otro', 'Otro'),
    ]

    codigo_espacio = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código del espacio',
        help_text='Ej: LAB-203',
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de espacio',
    )
    pabellon = models.CharField(
        max_length=100,
        verbose_name='Pabellón',
        help_text='Ej: Pabellón 1',
    )
    piso = models.CharField(
        max_length=20,
        verbose_name='Piso',
    )

    class Meta:
        db_table = 'espacios'
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['codigo_espacio']
        indexes = [
            models.Index(fields=['codigo_espacio'], name='idx_espacio_codigo'),
            models.Index(fields=['tipo'], name='idx_espacio_tipo'),
            models.Index(fields=['pabellon'], name='idx_espacio_pabellon'),
        ]

    def __str__(self):
        return f"{self.codigo_espacio} - {self.get_tipo_display()} ({self.pabellon})"
