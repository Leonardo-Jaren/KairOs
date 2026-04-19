from django.db import models
from equipos.models import Equipo
from mantenimiento.models import Mantenimiento


class Historial(models.Model): 
    id_historial = models.AutoField(primary_key=True)
    id_equipo_fk = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE,
        db_column='id_equipo_fk',
        related_name='historiales',
    )
    id_mantenimiento_fk = models.ForeignKey(
        Mantenimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_mantenimiento_fk',
        related_name='historiales',
    )
    fecha = models.DateTimeField()
    descripcion = models.TextField()
 
class Meta:
    db_table = 'historial'
    ordering = ['-fecha']  # Ordenar por fecha descendente

    def __str__(self):
        return f"Historial #{self.id_historial} - Equipo {self.id_equipo_fk_id} ({self.fecha})"  
