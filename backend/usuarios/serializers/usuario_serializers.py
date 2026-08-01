from rest_framework import serializers

from usuarios.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Representa datos públicos de una cuenta sin campos sensibles."""

    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'correo',
            'nombre',
            'apellido',
            'nombre_completo',
            'dni',
            'rol',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_nombre_completo(self, obj: Usuario) -> str:
        """Combina nombre y apellido para su presentación en tablas."""
        return f'{obj.nombre} {obj.apellido}'.strip()


class UsuarioCreateUpdateSerializer(serializers.ModelSerializer):
    """Valida el formato de los datos de escritura de usuarios."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        trim_whitespace=False,
        style={'input_type': 'password'},
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'correo',
            'nombre',
            'apellido',
            'dni',
            'rol',
            'password',
            'is_active',
        ]
        extra_kwargs = {
            'correo': {'validators': []},
            'username': {'validators': []},
        }

    def validate_correo(self, value: str) -> str:
        """Normaliza el correo antes de delegar su unicidad al service."""
        return value.strip().lower()

    def validate_dni(self, value: str | None) -> str | None:
        """Acepta únicamente DNI peruanos de ocho dígitos."""
        if value and (len(value) != 8 or not value.isdigit()):
            raise serializers.ValidationError('El DNI debe contener 8 dígitos.')
        return value
