from django.contrib import admin
from .models import ProductoSoftware, SoftwareInstalado


@admin.register(ProductoSoftware)
class ProductoSoftwareAdmin(admin.ModelAdmin):
    list_display = (
        'id_producto_software', 'software', 'version', 'tipo_licencia',
        'licencias_totales', 'licencias_disponibles', 'fecha_expiracion',
    )
    list_filter = ('tipo_licencia',)
    search_fields = ('software', 'version', 'descripcion')
    ordering = ('software', 'version')


@admin.register(SoftwareInstalado)
class SoftwareInstaladoAdmin(admin.ModelAdmin):
    list_display = (
        'id_instalacion', 'equipo', 'producto_software',
        'numero_licencia_usado', 'fecha_instalacion',
    )
    list_filter = ('fecha_instalacion',)
    search_fields = (
        'equipo__codigo', 'producto_software__software',
        'numero_licencia_usado',
    )
