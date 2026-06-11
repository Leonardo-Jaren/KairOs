from django.contrib import admin
from .models import Equipo, Componente


class ComponenteInline(admin.TabularInline):
    model = Componente
    extra = 1


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        'id_equipo', 'codigo', 'tipo_equipo',
        'marca', 'modelo', 'estado', 'espacio',
    )
    list_filter = ('tipo_equipo', 'estado', 'modo_adquisicion', 'marca')
    search_fields = ('codigo', 'numero_serie', 'numero_mac', 'marca', 'modelo')
    ordering = ('codigo',)
    inlines = [ComponenteInline]


@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ('id_componente', 'equipo', 'tipo', 'modelo', 'numero_serie')
    list_filter = ('tipo',)
    search_fields = ('modelo', 'descripcion', 'equipo__codigo')
