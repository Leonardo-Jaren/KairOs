from rest_framework import serializers

from espacios.models import Ciudad


class CiudadSerializer(serializers.ModelSerializer):
    """Representa una ciudad del catálogo."""

    class Meta:
        model = Ciudad
        fields = ['id', 'nombre']
        read_only_fields = fields


class CiudadCreateSerializer(serializers.ModelSerializer):
    """Valida el nombre usado para registrar una ciudad."""

    class Meta:
        model = Ciudad
        fields = ['nombre']

    def validate_nombre(self, value: str) -> str:
        nombre = ' '.join(value.split())
        if not Ciudad.normalizar_nombre(nombre):
            raise serializers.ValidationError('Ingresa el nombre de la ciudad.')
        return nombre
