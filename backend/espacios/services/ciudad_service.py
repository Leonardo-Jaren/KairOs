from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from espacios.models import Ciudad
from espacios.repositories.ciudad_repository import CiudadRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin


class CiudadService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para el catálogo de ciudades."""

    def __init__(self):
        self.repository = CiudadRepository()

    def listar(self, busqueda: str = ''):
        return self.repository.listar(busqueda=busqueda.strip())

    def _do_create(self, data: dict, actor=None):
        nombre = ' '.join(str(data.get('nombre', '')).split())
        nombre_normalizado = Ciudad.normalizar_nombre(nombre)
        if not nombre_normalizado:
            raise ValidationError({'nombre': 'Ingresa el nombre de la ciudad.'})

        existente = self.repository.get_by_nombre_normalizado(nombre_normalizado)
        if existente:
            if existente.is_deleted:
                return self.repository.restaurar(existente, actor), {'restored': True}
            raise ValidationError({
                'nombre': 'Ya existe una ciudad con ese nombre. Selecciónala del catálogo.'
            })

        try:
            with transaction.atomic():
                ciudad = self.repository.create(
                    nombre=nombre,
                    nombre_normalizado=nombre_normalizado,
                    created_by=actor,
                    updated_by=actor,
                )
        except IntegrityError as error:
            existente = self.repository.get_by_nombre_normalizado(nombre_normalizado)
            if existente:
                raise ValidationError({
                    'nombre': 'Ya existe una ciudad con ese nombre. Selecciónala del catálogo.'
                }) from error
            raise
        return ciudad, {'restored': False}

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        descripcion = (
            f'Ciudad {instance.nombre} reactivada.'
            if ctx.get('restored')
            else f'Ciudad {instance.nombre} registrada.'
        )
        self._audit_registrar(instance, 'ciudad.alta', actor, descripcion)
