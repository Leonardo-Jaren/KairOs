from django.contrib import admin
from .models import Ciudad, Edificio, Espacio, EspacioUsuario, Local


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    """Configura el catálogo normalizado de ciudades."""

    list_display = ('id', 'nombre', 'nombre_normalizado', 'is_deleted')
    search_fields = ('nombre', 'nombre_normalizado')
    ordering = ('nombre',)


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    """Configura la administración de locales físicos."""

    list_display = ('id', 'codigo', 'nombre', 'ciudad', 'tipo', 'activo')
    list_filter = ('ciudad', 'tipo', 'activo')
    search_fields = ('codigo', 'nombre', 'ciudad__nombre', 'descripcion')
    ordering = ('nombre', 'codigo')


@admin.register(Edificio)
class EdificioAdmin(admin.ModelAdmin):
    """Configura la administración de edificios del campus."""

    list_display = ('id', 'codigo', 'nombre', 'local', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre', 'descripcion', 'local__codigo', 'local__nombre')
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
