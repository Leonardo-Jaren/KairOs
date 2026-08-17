from django.contrib import admin
from .models import Incidencia


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'created_by', 'espacio', 'equipo', 'tipo_incidencia',
        'estado', 'created_at', 'fecha_resolucion', 'descripcion_corta',
    )
    list_filter = ('estado', 'tipo_incidencia', 'espacio')
    search_fields = (
        'descripcion', 'created_by__nombre',
        'equipo__codigo', 'espacio__codigo_espacio',
    )
    ordering = ('-created_at',)

    @admin.display(description='Descripción')
    def descripcion_corta(self, obj):
        return obj.descripcion[:80] + '...' if len(obj.descripcion) > 80 else obj.descripcion
