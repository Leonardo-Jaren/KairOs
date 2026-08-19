from django.contrib import admin
from .models import Edificio, Espacio, EspacioUsuario


@admin.register(Edificio)
class EdificioAdmin(admin.ModelAdmin):
    """Configura la administración de edificios del campus."""

    list_display = ('id', 'codigo', 'nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre', 'descripcion')
    ordering = ('nombre', 'codigo')


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'codigo_espacio',
        'tipo',
        'edificio',
        'pabellon',
        'piso',
        'activo',
    )
    list_filter = ('tipo', 'edificio', 'pabellon', 'piso', 'activo')
    search_fields = ('codigo_espacio', 'edificio__nombre', 'pabellon')
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
