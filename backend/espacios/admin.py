from django.contrib import admin
from .models import Espacio, EspacioUsuario


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo_espacio', 'tipo', 'pabellon', 'piso', 'activo')
    list_filter = ('tipo', 'pabellon', 'piso', 'activo')
    search_fields = ('codigo_espacio', 'pabellon')
    ordering = ('codigo_espacio',)


@admin.register(EspacioUsuario)
class EspacioUsuarioAdmin(admin.ModelAdmin):
    """Configura la consulta administrativa de asignaciones."""

    list_display = (
        'id',
        'espacio',
        'usuario',
        'tipo_responsabilidad',
        'activo',
    )
    list_filter = ('tipo_responsabilidad', 'activo')
    search_fields = (
        'espacio__codigo_espacio',
        'usuario__nombre',
        'usuario__correo',
    )
