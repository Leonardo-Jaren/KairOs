from django.contrib import admin
from .models import Incidencia


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = (
        'id_reporte', 'usuario', 'espacio', 'equipo',
        'prioridad', 'estado', 'fecha_generado',
    )
    list_filter  = ('estado', 'prioridad')
    search_fields = (
        'descripcion', 'usuario__nombre',
        'equipo__codigo', 'espacio__codigo_espacio',
    )
    ordering     = ('-fecha_generado',)
    readonly_fields = ('fecha_generado', 'fecha_asignacion', 'fecha_resolucion')
