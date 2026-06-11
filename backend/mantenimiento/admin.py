from django.contrib import admin
from .models import Mantenimiento, TecnicoMantenimiento


class TecnicoMantenimientoInline(admin.TabularInline):
    model = TecnicoMantenimiento
    extra = 1


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = (
        'id_mantenimiento', 'equipo', 'tipo_mantenimiento',
        'estado', 'fecha_inicio', 'fecha_cierre',
    )
    list_filter  = ('estado', 'tipo_mantenimiento')
    search_fields = ('equipo__codigo', 'descripcion')
    ordering     = ('-fecha_inicio',)
    inlines      = [TecnicoMantenimientoInline]


@admin.register(TecnicoMantenimiento)
class TecnicoMantenimientoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'mantenimiento', 'tecnico')
    list_filter   = ('tecnico__area',)
    search_fields = ('tecnico__usuario__nombre', 'mantenimiento__equipo__codigo')
