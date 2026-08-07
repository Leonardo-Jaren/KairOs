from rest_framework import serializers

from equipos.models import Componente


class ComponenteSerializer(serializers.ModelSerializer):
    """Representa un componente con sus datos de presentación."""

    tipo_display   = serializers.CharField(source='get_tipo_display', read_only=True)
    equipo_codigo  = serializers.CharField(source='equipo.codigo', read_only=True)

    class Meta:
        model = Componente
        fields = [
            'id',
            'equipo',
            'equipo_codigo',
            'tipo',
            'tipo_display',
            'modelo',
            'descripcion',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ComponenteCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos de creación y edición de un componente."""

    equipo_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Componente
        fields = ['equipo_id', 'tipo', 'modelo', 'descripcion']
        extra_kwargs = {
            'equipo_id':   {'required': False},
            'descripcion': {'required': False, 'allow_blank': True},
        }
