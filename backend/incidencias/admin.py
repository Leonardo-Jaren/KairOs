from django.contrib import admin
from .models import Incidencia


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'tecnico', 'docente', 'espacio', 'equipo',
        'fecha_generado', 'descripcion_corta',
    )
    list_filter = ('fecha_generado', 'espacio')
    search_fields = (
        'descripcion', 'tecnico__nombre', 'docente__nombre',
        'equipo__codigo', 'espacio__codigo_espacio',
    )
    ordering = ('-fecha_generado',)

    @admin.display(description='Descripción')
    def descripcion_corta(self, obj):
        return obj.descripcion[:80] + '...' if len(obj.descripcion) > 80 else obj.descripcion
