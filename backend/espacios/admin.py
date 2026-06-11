from django.contrib import admin
from .models import Pabellon, Espacio


@admin.register(Pabellon)
class PabellonAdmin(admin.ModelAdmin):
    list_display  = ('id_pabellon', 'nombre', 'total_pisos')
    search_fields = ('nombre',)
    ordering      = ('id_pabellon',)


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display  = ('id_espacio', 'codigo_espacio', 'tipo', 'pabellon', 'piso', 'capacidad')
    list_filter   = ('tipo', 'pabellon')
    search_fields = ('codigo_espacio',)
    ordering      = ('id_espacio',)
