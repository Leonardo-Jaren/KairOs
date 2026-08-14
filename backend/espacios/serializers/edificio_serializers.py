from rest_framework import serializers

from espacios.models import Edificio


class EdificioResumenSerializer(serializers.ModelSerializer):
    """Representa la identidad mínima de un edificio relacionado."""

    class Meta:
        model = Edificio
        fields = ['id', 'codigo', 'nombre', 'activo']


class EdificioSerializer(serializers.ModelSerializer):
    """Representa un edificio con sus contadores operativos."""

    cantidad_espacios = serializers.IntegerField(read_only=True, default=0)
    cantidad_pisos = serializers.IntegerField(read_only=True, default=0)
    cantidad_laboratorios = serializers.IntegerField(read_only=True, default=0)
    cantidad_aulas = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Edificio
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'activo',
            'cantidad_espacios',
            'cantidad_pisos',
            'cantidad_laboratorios',
            'cantidad_aulas',
            'created_at',
            'updated_at',
        ]


class EdificioCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos usados para crear o editar un edificio."""

    class Meta:
        model = Edificio
        fields = ['codigo', 'nombre', 'descripcion', 'activo']
        extra_kwargs = {
            'codigo': {'validators': []},
        }
