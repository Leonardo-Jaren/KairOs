from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from autenticacion.serializers.password_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from autenticacion.services.password_service import PasswordService


class PasswordResetRequestView(APIView):
    """
    Controlador para recibir la solicitud de recuperación de contraseña.
    Espera un correo electrónico y envía un enlace de recuperación.
    """
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_service = PasswordService()

    def post(self, request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        correo = serializer.validated_data['correo']
        
        # Siempre respondemos 200 OK para evitar enumeración de correos
        self.password_service.request_password_reset(correo)
        
        return Response(
            {"detail": "Hemos enviado un enlace para recuperar la contraseña."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Controlador para confirmar y establecer la nueva contraseña.
    Espera el uidb64, el token generado, y la nueva contraseña.
    """
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_service = PasswordService()

    def post(self, request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']
        
        success = self.password_service.validate_token_and_reset(uidb64, token, new_password)
        
        if success:
            return Response(
                {"detail": "Contraseña restablecida exitosamente."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "El enlace de recuperación es inválido o ha expirado."},
                status=status.HTTP_400_BAD_REQUEST
            )
