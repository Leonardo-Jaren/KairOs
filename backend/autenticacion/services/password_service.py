from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

from common.base_service import BaseService
from usuarios.services.usuario_service import UsuarioService


class PasswordService(BaseService):
    """
    Servicio de lógica de negocio para la gestión de recuperación de contraseñas.
    Cumple con SRP manejando exclusivamente validación de tokens y envío de emails.
    """
    def __init__(self):
        self.usuario_service = UsuarioService()
        self.token_generator = PasswordResetTokenGenerator()

    def request_password_reset(self, correo: str) -> None:
        """
        Inicia el flujo de recuperación de contraseña si el correo existe.
        """
        user = self.usuario_service.get_by_correo(correo)
        if not user or not user.is_active:
            # Por seguridad, no lanzamos error si el usuario no existe para evitar enumeración.
            return

        # Generar token y uid (uidb64)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = self.token_generator.make_token(user)

        # TODO: En un ambiente real, extraer esto del frontend URL configurado en entorno
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        reset_url = f"{frontend_url}/reset-password/{uidb64}/{token}"

        # Enviar correo
        subject = "Recuperación de contraseña en KairOs"
        message = f"Hola {user.nombre},\n\nPara restablecer tu contraseña, visita el siguiente enlace:\n\n{reset_url}\n\nSi no solicitaste esto, ignora este correo."
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@kairos.com'),
            recipient_list=[user.correo],
            fail_silently=False,
        )

    def validate_token_and_reset(self, uidb64: str, token: str, new_password: str) -> bool:
        """
        Valida el token y en caso afirmativo, actualiza la contraseña del usuario.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = self.usuario_service.get_by_id(uid)
        except (TypeError, ValueError, OverflowError):
            return False

        if user is None:
            return False

        if not self.token_generator.check_token(user, token):
            return False

        # Reset password
        user.set_password(new_password)
        user.save()
        return True
