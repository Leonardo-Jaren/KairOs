from django.contrib import admin
from .models import Historial


@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = (
        'id_historial', 'tabla_afectada', 'registro_id',
        'accion', 'usuario', 'ip_address', 'fecha',
    )
    list_filter   = ('accion', 'tabla_afectada')
    search_fields = ('tabla_afectada', 'usuario__nombre', 'ip_address')
    ordering      = ('-fecha',)

    # El historial es inmutable; ningún campo debe ser editable desde el admin
    readonly_fields = (
        'id_historial', 'usuario', 'accion', 'tabla_afectada',
        'registro_id', 'datos_anteriores', 'datos_nuevos',
        'ip_address', 'fecha',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
