from django.contrib import admin
from .models import Historial


@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipo', 'mantenimiento', 'fecha', 'descripcion_corta')
    list_filter = ('fecha',)
    search_fields = ('equipo__codigo', 'descripcion')
    ordering = ('-fecha',)

    @admin.display(description='Descripción')
    def descripcion_corta(self, obj):
        return obj.descripcion[:80] + '...' if len(obj.descripcion) > 80 else obj.descripcion
