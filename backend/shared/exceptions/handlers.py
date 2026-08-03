from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Normaliza todos los errores de la API a un formato JSON consistente:
    - Errores de validación (400): {"errores": {"campo": ["mensaje"]}}
    - Autenticación, permisos, not found: {"error": "mensaje"}
    - Error no capturado (500): {"error": "Error interno del servidor."}
    """
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {'error': 'Error interno del servidor.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValidationError):
        response.data = {'errores': response.data}
    elif isinstance(response.data, dict) and 'detail' in response.data:
        response.data = {'error': str(response.data['detail'])}

    return response
