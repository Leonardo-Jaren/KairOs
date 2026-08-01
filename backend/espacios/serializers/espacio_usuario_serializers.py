from rest_framework import serializers

from espacios.models import Espacio, EspacioUsuario
from usuarios.models import Usuario


class UsuarioResumenSerializer(serializers.ModelSerializer):
    """Representa los datos mínimos del usuario asignado."""

    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_completo', 'correo', 'rol']

    def get_nombre_completo(self, obj: Usuario) -> str:
        """Combina nombres y apellidos para presentación."""
        return f'{obj.nombre} {obj.apellido}'.strip()


class EspacioResumenSerializer(serializers.ModelSerializer):
    """Representa los datos mínimos del espacio asignado."""

    tipo_display = serializers.CharField(source='get_tipo_display')

    class Meta:
        model = Espacio
        fields = [
            'id',
            'codigo_espacio',
            'tipo',
            'tipo_display',
            'pabellon',
            'piso',
        ]


class EspacioUsuarioSerializer(serializers.ModelSerializer):
    """Representa una asignación con sus relaciones expandidas."""

    usuario = UsuarioResumenSerializer(read_only=True)
    espacio = EspacioResumenSerializer(read_only=True)
    tipo_responsabilidad_display = serializers.CharField(
        source='get_tipo_responsabilidad_display',
        read_only=True,
    )

    class Meta:
        model = EspacioUsuario
        fields = [
            'id',
            'usuario',
            'espacio',
            'tipo_responsabilidad',
            'tipo_responsabilidad_display',
            'activo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class EspacioUsuarioCreateUpdateSerializer(serializers.Serializer):
    """Valida el formato de una asignación antes de aplicar reglas."""

    usuario_id = serializers.IntegerField(min_value=1, required=False)
    espacio_id = serializers.IntegerField(min_value=1, required=False)
    tipo_responsabilidad = serializers.ChoiceField(
        choices=EspacioUsuario.TIPO_RESPONSABILIDAD_CHOICES,
        required=False,
        default='responsable',
    )
    activo = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        """Exige ambas relaciones durante la creación."""
        if self.instance is None:
            errors = {}
            if 'usuario_id' not in attrs:
                errors['usuario_id'] = 'Este campo es obligatorio.'
            if 'espacio_id' not in attrs:
                errors['espacio_id'] = 'Este campo es obligatorio.'
            if errors:
                raise serializers.ValidationError(errors)
        return attrs
