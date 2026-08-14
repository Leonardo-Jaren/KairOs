from rest_framework.exceptions import ValidationError

from espacios.models import Edificio
from espacios.repositories.edificio_repository import EdificioRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario


class EdificioService(AuditableMixin, BaseService):
    """Aplica las reglas para administrar los edificios del campus."""

    ALTA = 'edificio.alta'
    ACTUALIZACION = 'edificio.actualizacion'
    DESACTIVACION = 'edificio.desactivacion'

    def __init__(self):
        self.repository = EdificioRepository()

    def listar(self, busqueda: str = '', activo: bool | None = None):
        """Lista edificios aplicando filtros normalizados."""
        return self.repository.listar(
            busqueda=busqueda.strip(),
            activo=activo,
        )

    def get_estadisticas(self) -> dict:
        """Entrega los indicadores generales de edificios."""
        return self.repository.get_estadisticas()

    def _do_create(self, data: dict, actor: Usuario = None):
        clean_data = self._normalizar(data)
        existing = self.repository.get_by_codigo(clean_data['codigo'])
        if existing and existing.is_deleted:
            instance = self.repository.restore(existing, clean_data, actor)
            return instance, {'restored': True}
        self._validar_codigo(clean_data['codigo'])
        instance = self.repository.create(
            **clean_data,
            created_by=actor,
            updated_by=actor,
        )
        return self.repository.get_by_id(instance.id), {'restored': False}

    def _do_update(self, id: int, data: dict, actor: Usuario = None) -> Edificio:
        instance = self.get_by_id(id)
        clean_data = self._normalizar(data, partial=True)
        codigo = clean_data.get('codigo', instance.codigo)
        self._validar_codigo(codigo, exclude_id=instance.id)
        clean_data['updated_by'] = actor
        self.repository.update_with_spaces(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def _do_delete(self, id: int, actor: Usuario = None) -> Edificio:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        descripcion = (
            f'Edificio {instance.codigo} reactivado.'
            if ctx.get('restored')
            else f'Edificio {instance.codigo} registrado.'
        )
        self._audit_registrar(instance, self.ALTA, actor, descripcion)

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        if cambios:
            self._audit_registrar(
                instance,
                self.ACTUALIZACION,
                actor,
                f'Edificio {instance.codigo} actualizado.',
                datos_extra={'cambios': cambios},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(
            instance,
            self.DESACTIVACION,
            actor,
            f'Edificio {instance.codigo} desactivado.',
        )

    def _normalizar(self, data: dict, partial: bool = False) -> dict:
        clean_data = data.copy()
        if 'codigo' in clean_data:
            clean_data['codigo'] = clean_data['codigo'].strip().upper()
        elif not partial:
            clean_data['codigo'] = ''
        for field in ['nombre', 'descripcion']:
            if field in clean_data:
                clean_data[field] = clean_data[field].strip()
        return clean_data

    def _validar_codigo(self, codigo: str, exclude_id: int | None = None) -> None:
        if self.repository.get_by_codigo(codigo, exclude_id):
            raise ValidationError({'codigo': 'Ya existe un edificio con este código.'})
