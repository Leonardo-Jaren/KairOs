from django.contrib import admin
from .models import Mantenimiento, TecnicoMantenimiento


class TecnicoMantenimientoInline(admin.TabularInline):
    model = TecnicoMantenimiento
    extra = 1


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'equipo', 'fecha', 'tipo_mantenimiento',
        'estado', 'reportado_por', 'descripcion_corta',
    )
    list_filter = ('tipo_mantenimiento', 'estado', 'fecha')
    search_fields = ('equipo__codigo', 'descripcion')
    ordering = ('-fecha',)
    inlines = [TecnicoMantenimientoInline]

    @admin.display(description='Descripción')
    def descripcion_corta(self, obj):
        return obj.descripcion[:80] + '...' if len(obj.descripcion) > 80 else obj.descripcion


@admin.register(TecnicoMantenimiento)
class TecnicoMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mantenimiento', 'tecnico')
    list_filter = ('tecnico__area',)
    search_fields = ('tecnico__usuario__nombre', 'mantenimiento__equipo__codigo')
