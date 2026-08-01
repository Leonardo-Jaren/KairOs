from rest_framework import serializers
from usuarios.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer de salida para representar los datos de un usuario.
    Excluye campos de seguridad sensibles como contraseñas.
    """
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'correo',
            'nombre',
            'apellido',
            'dni',
            'rol',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UsuarioCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer de entrada para validar datos de creación y actualización de usuarios.
    """
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'},
        help_text='Contraseña para el usuario. Dejar en blanco si inicia sesión con Google.'
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
            'is_active'
        ]

    def validate_correo(self, value: str) -> str:
        """
        Valida que el correo electrónico sea único en el sistema.
        """
        # Obtenemos la instancia actual para excluirla en caso de actualización
        instance = self.instance
        queryset = Usuario.objects.filter(correo=value)
        if instance:
            queryset = queryset.exclude(id=instance.id)
            
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un usuario registrado con este correo electrónico.")
        return value

    def validate_username(self, value: str) -> str:
        """
        Valida que el nombre de usuario (username) sea único en el sistema.
        """
        instance = self.instance
        queryset = Usuario.objects.filter(username=value)
        if instance:
            queryset = queryset.exclude(id=instance.id)
            
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un usuario registrado con este nombre de usuario.")
        return value

    def validate(self, attrs):
        """
        Valida que un técnico solo pueda registrar o modificar usuarios con rol 'docente'.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.rol == 'tecnico':
                # Al actualizar o crear, el rol debe ser docente
                rol = attrs.get('rol')
                if rol and rol != 'docente':
                    raise serializers.ValidationError({
                        "rol": "Los técnicos solo tienen autorización para registrar usuarios con el rol de Docente."
                    })
        return attrs
