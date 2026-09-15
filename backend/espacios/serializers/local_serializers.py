from rest_framework import serializers

from espacios.models import Local


class LocalResumenSerializer(serializers.ModelSerializer):
    """Representa los datos mínimos de un local relacionado."""

    class Meta:
        model = Local
        fields = ['id', 'codigo', 'nombre', 'ciudad', 'activo']


class LocalSerializer(serializers.ModelSerializer):
    """Representa un local con sus datos auditables de consulta."""

    class Meta:
        model = Local
        fields = [
            'id',
            'codigo',
            'nombre',
            'ciudad',
            'descripcion',
            'activo',
            'created_at',
            'updated_at',
        ]


class LocalCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos usados para crear o editar un local."""

    class Meta:
        model = Local
        fields = ['codigo', 'nombre', 'ciudad', 'descripcion', 'activo']
        extra_kwargs = {
            'codigo': {'validators': []},
        }
