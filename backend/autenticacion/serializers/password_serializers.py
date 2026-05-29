from rest_framework import serializers

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer para validar la solicitud de envío de correo de recuperación.
    """
    correo = serializers.EmailField(
        required=True,
        error_messages={'required': 'El correo electrónico es obligatorio.'}
    )


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer para validar el payload de confirmación de recuperación de contraseña.
    """
    uidb64 = serializers.CharField(
        required=True,
        error_messages={'required': 'El parámetro uidb64 es obligatorio.'}
    )
    token = serializers.CharField(
        required=True,
        error_messages={'required': 'El token es obligatorio.'}
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        error_messages={
            'required': 'La nueva contraseña es obligatoria.',
            'min_length': 'La contraseña debe tener al menos 8 caracteres.'
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={'required': 'Debes confirmar la nueva contraseña.'}
    )

    def validate(self, data):
        """
        Asegura que ambas contraseñas coincidan.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        return data
