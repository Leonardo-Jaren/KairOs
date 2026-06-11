from rest_framework import serializers
from mantenimiento.models import Mantenimiento, TecnicoMantenimiento


class PerfilTecnicoResumenSerializer(serializers.Serializer):
    """ISP — expone sólo los campos que el contexto de mantenimiento necesita."""

    id_tecnico = serializers.IntegerField()
    area       = serializers.CharField()
    nombre     = serializers.SerializerMethodField()

    def get_nombre(self, obj):
        return obj.usuario.nombre if obj.usuario else None


class TecnicoMantenimientoReadSerializer(serializers.ModelSerializer):
    tecnico = PerfilTecnicoResumenSerializer(read_only=True)

    class Meta:
        model  = TecnicoMantenimiento
        fields = ['id', 'tecnico']


class MantenimientoReadSerializer(serializers.ModelSerializer):
    tecnicos_asignados    = TecnicoMantenimientoReadSerializer(many=True, read_only=True)
    equipo_codigo         = serializers.CharField(source='equipo.codigo', read_only=True)
    usuario_cierre_nombre = serializers.SerializerMethodField()

    class Meta:
        model  = Mantenimiento
        fields = [
            'id_mantenimiento',
            'equipo', 'equipo_codigo',
            'fecha_inicio', 'fecha_cierre',
            'tipo_mantenimiento', 'estado',
            'descripcion', 'observaciones_cierre',
            'usuario_cierre', 'usuario_cierre_nombre',
            'tecnicos_asignados',
        ]

    def get_usuario_cierre_nombre(self, obj):
        return obj.usuario_cierre.nombre if obj.usuario_cierre else None


class MantenimientoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mantenimiento
        fields = ['equipo', 'tipo_mantenimiento', 'descripcion', 'fecha_inicio']
        extra_kwargs = {
            'tipo_mantenimiento': {'required': False},
            'descripcion':        {'required': False},
            'fecha_inicio':       {'required': False},
        }


class MantenimientoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mantenimiento
        fields = ['tipo_mantenimiento', 'descripcion']
        extra_kwargs = {
            'tipo_mantenimiento': {'required': False},
            'descripcion':        {'required': False},
        }


class MantenimientoCerrarSerializer(serializers.Serializer):
    observaciones_cierre = serializers.CharField(required=False, allow_blank=True)


class AsignarTecnicoSerializer(serializers.Serializer):
    id_tecnico = serializers.IntegerField()
