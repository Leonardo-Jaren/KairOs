from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """
    Modelo base abstracto que provee campos de auditoría y borrado lógico
    para todos los modelos del sistema.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Creado por'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='Actualizado por'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Eliminado (Soft Delete)'
    )

    class Meta:
        abstract = True
