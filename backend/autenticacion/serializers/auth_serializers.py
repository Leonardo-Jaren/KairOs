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
    Serializer para devolver información del perfil de usuario en la respuesta de autenticación.
    """
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    apellido = serializers.CharField(required=False, default='', allow_blank=True)
    correo = serializers.EmailField()
    rol = serializers.CharField()
    username = serializers.CharField()
    is_superuser = serializers.BooleanField(default=False)
    sedes = serializers.SerializerMethodField()
    permisos_efectivos = serializers.SerializerMethodField()

    def get_sedes(self, obj) -> list:
        if not hasattr(obj, 'usuario_sedes'):
            return []
        return [
            {
                'id': us.local.id,
                'codigo': us.local.codigo,
                'nombre': us.local.nombre,
                'ciudad': us.local.ciudad,
                'es_sede_principal': us.es_sede_principal,
            }
            for us in obj.usuario_sedes.all()
            if us.activo and hasattr(us, 'local') and us.local
        ]

    def get_permisos_efectivos(self, obj) -> dict:
        if hasattr(obj, 'get_permisos_efectivos'):
            return obj.get_permisos_efectivos()
        return {}



class UserAuthResponseSerializer(serializers.Serializer):
    """
    Serializer de salida que unifica los tokens JWT y la información básica del usuario autenticado.
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    usuario = UserProfileSerializer()
