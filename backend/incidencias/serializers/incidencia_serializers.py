from rest_framework import serializers
from incidencias.models import Incidencia


class TecnicoResumenSerializer(serializers.Serializer):
    """ISP — expone sólo lo que el contexto de incidencias necesita del técnico."""

    id_tecnico = serializers.IntegerField()
    area       = serializers.CharField()
    nombre     = serializers.SerializerMethodField()

    def get_nombre(self, obj):
        return obj.usuario.nombre if obj.usuario else None


class IncidenciaReadSerializer(serializers.ModelSerializer):
    usuario_nombre   = serializers.SerializerMethodField()
    espacio_codigo   = serializers.CharField(source='espacio.codigo_espacio', read_only=True, default=None)
    equipo_codigo    = serializers.CharField(source='equipo.codigo',          read_only=True, default=None)
    tecnico_asignado = TecnicoResumenSerializer(read_only=True)
    mantenimiento_id = serializers.IntegerField(
        source='mantenimiento.id_mantenimiento',
        read_only=True,
        default=None,
    )

    class Meta:
        model  = Incidencia
        fields = [
            'id_reporte',
            'usuario', 'usuario_nombre',
            'espacio', 'espacio_codigo',
            'equipo',  'equipo_codigo',
            'fecha_generado',
            'descripcion',
            'estado', 'prioridad',
            'tecnico_asignado', 'fecha_asignacion',
            'solucion', 'fecha_resolucion',
            'mantenimiento', 'mantenimiento_id',
        ]

    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre if obj.usuario else None


class IncidenciaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Incidencia
        fields = ['espacio', 'equipo', 'descripcion', 'prioridad']
        extra_kwargs = {
            'equipo':    {'required': False},
            'prioridad': {'required': False},
        }


class AsignarTecnicoSerializer(serializers.Serializer):
    id_tecnico = serializers.IntegerField()


class ResolverIncidenciaSerializer(serializers.Serializer):
    solucion = serializers.CharField()


class VincularMantenimientoSerializer(serializers.Serializer):
    id_mantenimiento = serializers.IntegerField()
