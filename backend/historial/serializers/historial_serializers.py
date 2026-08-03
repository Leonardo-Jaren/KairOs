from rest_framework import serializers

from historial.models import Historial


class HistorialSerializer(serializers.ModelSerializer):
    """Representa un evento de auditoría para consumo del frontend."""

    usuario_nombre = serializers.SerializerMethodField()
    modulo = serializers.SerializerMethodField()

    class Meta:
        model = Historial
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'fecha',
            'tipo_evento',
            'modulo',
            'object_id',
            'descripcion',
            'datos_extra',
        ]
        read_only_fields = fields

    def get_usuario_nombre(self, obj: Historial) -> str | None:
        """Retorna el nombre completo del usuario que generó el evento."""
        if obj.usuario:
            return f'{obj.usuario.nombre} {obj.usuario.apellido}'.strip()
        return None

    def get_modulo(self, obj: Historial) -> str:
        """Retorna el nombre del modelo auditado en minúsculas."""
        return obj.content_type.model
