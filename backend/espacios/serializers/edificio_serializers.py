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
            'configuracion_croquis',
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


class CroquisAmbienteSerializer(serializers.Serializer):
    """Valida la posición y el tamaño de un ambiente dentro del piso."""

    espacio_id = serializers.IntegerField(min_value=1)
    fila = serializers.IntegerField(min_value=1, max_value=12)
    columna = serializers.IntegerField(min_value=1, max_value=16)
    ancho = serializers.IntegerField(min_value=1, max_value=6)
    alto = serializers.IntegerField(min_value=1, max_value=4)


class CeldaPasilloSerializer(serializers.Serializer):
    """Representa una celda transitable del croquis."""

    fila = serializers.IntegerField(min_value=1, max_value=12)
    columna = serializers.IntegerField(min_value=1, max_value=16)


class CroquisPisoSerializer(serializers.Serializer):
    """Valida la cuadrícula editable de un piso del edificio."""

    piso = serializers.RegexField(
        regex=r'^\d+$',
        max_length=20,
        error_messages={
            'invalid': 'El piso debe contener únicamente números.',
        },
    )
    filas = serializers.IntegerField(min_value=3, max_value=12)
    columnas = serializers.IntegerField(min_value=6, max_value=16)
    ambientes = CroquisAmbienteSerializer(many=True, allow_empty=True)
    pasillos = CeldaPasilloSerializer(many=True, allow_empty=True)

    def validate(self, attrs):
        """Evita identificadores de ambiente y celdas de pasillo repetidas."""
        space_ids = [item['espacio_id'] for item in attrs['ambientes']]
        if len(space_ids) != len(set(space_ids)):
            raise serializers.ValidationError({
                'ambientes': 'Cada ambiente puede aparecer una sola vez en el croquis.'
            })
        corridor_cells = [
            (item['fila'], item['columna']) for item in attrs['pasillos']
        ]
        if len(corridor_cells) != len(set(corridor_cells)):
            raise serializers.ValidationError({
                'pasillos': 'Una celda de pasillo no puede repetirse.'
            })
        return attrs
