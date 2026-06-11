from rest_framework import serializers
from historial.models import Historial


class HistorialReadSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model  = Historial
        fields = [
            'id_historial',
            'usuario', 'usuario_nombre',
            'accion',
            'tabla_afectada', 'registro_id',
            'datos_anteriores', 'datos_nuevos',
            'ip_address',
            'fecha',
        ]

    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre if obj.usuario else None
