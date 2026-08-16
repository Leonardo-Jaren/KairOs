from typing import Any

from rest_framework.exceptions import ValidationError

from shared.base import BaseService
from shared.mixins import AuditableMixin
from software.repositories import ProductoSoftwareRepository


class ProductoSoftwareService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio del catalogo de software."""

    ALTA          = 'software.alta'
    BAJA          = 'software.baja'
    ACTUALIZACION = 'software.actualizacion'

    def __init__(self):
        self.repository = ProductoSoftwareRepository()

    def listar(self, busqueda: str = '', tipo_licencia: str = ''):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            tipo_licencia=tipo_licencia.strip(),
        )

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Any = None) -> Any:
        clean_data = self._normalizar(data)
        self._validar_unicidad(clean_data)
        instance = self.repository.create(**clean_data, created_by=actor, updated_by=actor)
        return self.repository.get_by_id(instance.id)

    def _do_update(self, id: int, data: dict, actor: Any = None) -> Any:
        instance = self.get_by_id(id)
        clean_data = self._normalizar(data, partial=True)
        self._validar_unicidad(clean_data, exclude_id=instance.id)
        self._validar_reduccion_licencias(instance, clean_data)
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def _do_delete(self, id: int, actor: Any = None) -> Any:
        instance = self.get_by_id(id)
        if instance.licencias_usadas > 0:
            raise ValidationError(
                {'detail': 'No se puede eliminar un producto con instalaciones vigentes.'}
            )
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        self._audit_registrar(instance, self.ALTA, actor, f'Software {instance} registrado.')

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        if cambios:
            self._audit_registrar(
                instance, self.ACTUALIZACION, actor,
                f'Software {instance} actualizado.',
                datos_extra={'cambios': cambios},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(instance, self.BAJA, actor, f'Software {instance} dado de baja.')

    def get_estadisticas(self) -> dict:
        """Retorna indicadores para la cabecera del modulo."""
        return self.repository.get_estadisticas()

    def get_opciones(self):
        """Retorna productos de software vigentes para poblar selects de otros modulos."""
        return self.repository.get_opciones()

    def _normalizar(self, data: dict, partial: bool = False) -> dict:
        clean_data = data.copy()
        if 'software' in clean_data:
            clean_data['software'] = clean_data['software'].strip()
        if 'version' in clean_data:
            clean_data['version'] = clean_data['version'].strip()
        return clean_data

    def _validar_unicidad(self, data: dict, exclude_id: int | None = None) -> None:
        """Valida campos unicos sin acceder al ORM fuera del repository."""
        software = data.get('software')
        version = data.get('version')
        if not software or not version:
            return

        if self.repository.get_by_nombre_version(software, version, exclude_id):
            raise ValidationError(
                {'software': 'Ya existe un producto con este software y version.'}
            )

    def _validar_reduccion_licencias(self, instance: Any, data: dict) -> None:
        """Impide reducir licencias_totales por debajo de las instalaciones vigentes."""
        if 'licencias_totales' not in data:
            return
        if data['licencias_totales'] < instance.licencias_usadas:
            raise ValidationError(
                {
                    'licencias_totales': (
                        'No se puede reducir por debajo de las instalaciones vigentes '
                        f'({instance.licencias_usadas}).'
                    )
                }
            )
