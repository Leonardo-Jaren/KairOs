from rest_framework import serializers

from equipos.models import Equipo


class EquipoSerializer(serializers.ModelSerializer):
    """Representa un equipo con sus indicadores de presentacion."""

    tipo_equipo_display = serializers.CharField(source='get_tipo_equipo_display', read_only=True)
    modo_adquisicion_display = serializers.CharField(source='get_modo_adquisicion_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    espacio_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Equipo
        fields = [
            'id',
            'espacio',
            'espacio_nombre',
            'codigo',
            'numero_serie',
            'numero_mac',
            'tipo_equipo',
            'tipo_equipo_display',
            'marca',
            'modelo',
            'modo_adquisicion',
            'modo_adquisicion_display',
            'fecha_adquisicion',
            'fecha_renovacion',
            'estado',
            'estado_display',
            'responsable_usuario',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_espacio_nombre(self, obj: Equipo) -> str | None:
        """Combina codigo y pabellon del espacio asignado."""
        if not obj.espacio_id:
            return None
        return f'{obj.espacio.codigo_espacio} - {obj.espacio.pabellon}'


class EquipoCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos de creacion y edicion de un equipo."""

    class Meta:
        model = Equipo
        fields = [
            'espacio',
            'codigo',
            'numero_serie',
            'numero_mac',
            'tipo_equipo',
            'marca',
            'modelo',
            'modo_adquisicion',
            'fecha_adquisicion',
            'fecha_renovacion',
            'estado',
            'responsable_usuario',
        ]
        extra_kwargs = {
            'codigo': {'validators': []},
            'numero_serie': {'validators': []},
            'espacio': {'required': False, 'allow_null': True},
            'fecha_renovacion': {'required': False, 'allow_null': True},
        }
