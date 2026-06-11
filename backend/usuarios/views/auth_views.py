from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from usuarios.serializers.auth_serializers import (
    LoginSerializer,
    LogoutSerializer,
    TokenRefreshSerializer,
)
from usuarios.services.auth_service import AuthService
from usuarios.repositories.user_repository import UserRepository
from usuarios.exceptions import AutenticacionError


class LoginView(APIView):
    """POST /auth/login/ — cualquiera puede intentar autenticarse."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthService(UserRepository())
        try:
            usuario = service.authenticate(
                correo=serializer.validated_data["correo"],
                password=serializer.validated_data["password"],
            )
            tokens = service.generate_tokens(usuario)
            return Response(tokens, status=status.HTTP_200_OK)

        except AutenticacionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """POST /auth/logout/ — blacklistea el refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthService(UserRepository())
        try:
            service.logout(serializer.validated_data["refresh"])
            return Response(status=status.HTTP_204_NO_CONTENT)

        except AutenticacionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    """POST /auth/token/refresh/ — renueva el access token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthService(UserRepository())
        try:
            tokens = service.refresh_access_token(serializer.validated_data["refresh"])
            return Response(tokens, status=status.HTTP_200_OK)

        except AutenticacionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
