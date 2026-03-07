from django.contrib import admin
from .models import Espacio


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo_espacio', 'tipo', 'pabellon', 'piso')
    list_filter = ('tipo', 'pabellon', 'piso')
    search_fields = ('codigo_espacio', 'pabellon')
    ordering = ('codigo_espacio',)
