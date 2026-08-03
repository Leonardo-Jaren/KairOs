from django.contrib import admin

from historial.models import Historial


@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_evento', 'modulo_display', 'object_id', 'usuario', 'fecha')
    list_filter = ('tipo_evento', 'fecha')
    search_fields = ('tipo_evento', 'descripcion', 'usuario__nombre')
    ordering = ('-fecha',)
    readonly_fields = (
        'tipo_evento', 'content_type', 'object_id',
        'usuario', 'fecha', 'descripcion', 'datos_extra',
    )

    @admin.display(description='Módulo')
    def modulo_display(self, obj: Historial) -> str:
        return obj.content_type.model
