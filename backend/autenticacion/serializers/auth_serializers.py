from rest_framework import serializers


class LocalLoginSerializer(serializers.Serializer):
    """
    Validador para el inicio de sesión tradicional con correo y contraseña.
    """
    correo = serializers.EmailField(
        required=True,
        error_messages={'required': 'El correo electrónico es obligatorio.'}
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        error_messages={'required': 'La contraseña es obligatoria.'}
    )


class GoogleLoginSerializer(serializers.Serializer):
    """
    Validador del payload enviado por el frontend al iniciar sesión con Google.
    El campo 'token' corresponde al ID Token (JWT) emitido por Google Identity Services.
    """
    token = serializers.CharField(
        required=True,
        error_messages={'required': 'El ID Token de Google es obligatorio.'}
    )


class UserProfileSerializer(serializers.Serializer):
    """
    Serializer simple para devolver información del perfil de usuario en la respuesta de autenticación.
    """
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    correo = serializers.EmailField()
    rol = serializers.CharField()
    username = serializers.CharField()


class UserAuthResponseSerializer(serializers.Serializer):
    """
    Serializer de salida que unifica los tokens JWT y la información básica del usuario autenticado.
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    usuario = UserProfileSerializer()
