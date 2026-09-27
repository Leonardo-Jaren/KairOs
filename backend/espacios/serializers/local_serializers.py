from rest_framework import serializers

from espacios.models import Ciudad, Local


class LocalResumenSerializer(serializers.ModelSerializer):
    """Representa los datos mínimos de un local relacionado."""

    ciudad = serializers.CharField(source='ciudad.nombre', read_only=True, allow_null=True)
    ciudad_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = Local
        fields = ['id', 'codigo', 'nombre', 'ciudad', 'ciudad_id', 'tipo', 'activo']


class LocalSerializer(serializers.ModelSerializer):
    """Representa un local con sus datos auditables de consulta."""

    ciudad = serializers.CharField(source='ciudad.nombre', read_only=True, allow_null=True)
    ciudad_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = Local
        fields = [
            'id',
            'codigo',
            'nombre',
            'ciudad',
            'ciudad_id',
            'tipo',
            'descripcion',
            'activo',
            'created_at',
            'updated_at',
        ]


class LocalCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida los datos usados para crear o editar un local."""

    ciudad = serializers.CharField(source='ciudad.nombre', read_only=True, allow_null=True)
    ciudad_id = serializers.PrimaryKeyRelatedField(
        source='ciudad',
        queryset=Ciudad.objects.filter(is_deleted=False),
        error_messages={
            'does_not_exist': 'Selecciona una ciudad vigente del catálogo.',
            'incorrect_type': 'Selecciona una ciudad vigente del catálogo.',
        },
    )

    class Meta:
        model = Local
        fields = ['codigo', 'nombre', 'ciudad', 'ciudad_id', 'tipo', 'descripcion', 'activo']
        extra_kwargs = {
            'codigo': {'validators': []},
        }
