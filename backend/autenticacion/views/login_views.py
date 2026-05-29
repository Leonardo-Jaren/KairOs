from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from autenticacion.serializers.auth_serializers import (
    LocalLoginSerializer,
    GoogleLoginSerializer,
    UserAuthResponseSerializer
)
from autenticacion.services.google_auth_service import GoogleAuthService
from autenticacion.services.token_service import TokenService
from usuarios.services.usuario_service import UsuarioService


class LocalLoginView(APIView):
    """
    Controlador encargado del inicio de sesión local mediante correo y contraseña.
    Implementa SRP al delegar la lógica de tokens y base de datos a sus respectivos servicios.
    """
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_service = UsuarioService()
        self.token_service = TokenService()

    def post(self, request) -> Response:
        serializer = LocalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        correo = serializer.validated_data['correo']
        password = serializer.validated_data['password']
        
        # Buscar usuario e intentar validar credenciales
        user = self.usuario_service.get_by_correo(correo)
        if user is None or not user.check_password(password):
            return Response(
                {"detail": "Credenciales inválidas. Por favor verifique el correo electrónico y la contraseña."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # Validar si el usuario se encuentra activo
        if not user.is_active:
            return Response(
                {"detail": "Su cuenta de usuario está desactivada. Comuníquese con el administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Generar Access y Refresh tokens
        tokens = self.token_service.generate_tokens_for_user(user)
        
        response_payload = {
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'usuario': user
        }
        
        output_serializer = UserAuthResponseSerializer(response_payload)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    """
    Controlador encargado del inicio de sesión federado por medio de Google.
    Recibe el token provisto por el frontend, lo verifica y retorna tokens locales.
    """
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.google_auth_service = GoogleAuthService()
        self.usuario_service = UsuarioService()
        self.token_service = TokenService()

    def post(self, request) -> Response:
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        
        # 1. Validar el token externamente en Google
        try:
            google_profile = self.google_auth_service.verify_token(token)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        correo = google_profile['correo']
        nombre = google_profile['nombre']
        
        # 2. Buscar o crear el usuario de forma segura
        user = self.usuario_service.get_by_correo(correo)
        if user is None:
            # Creación dinámica (Auto-registro) para usuarios nuevos
            user = self.usuario_service.create_google_user(correo, nombre)
        else:
            # Comprobar que esté activo
            if not user.is_active:
                return Response(
                    {"detail": "Su cuenta de usuario está desactivada. Comuníquese con el administrador."},
                    status=status.HTTP_403_FORBIDDEN
                )
                
        # 3. Generar Access y Refresh tokens para la sesión local
        tokens = self.token_service.generate_tokens_for_user(user)
        
        response_payload = {
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'usuario': user
        }
        
        output_serializer = UserAuthResponseSerializer(response_payload)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
