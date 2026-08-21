from typing import Any

from rest_framework.exceptions import ValidationError

from shared.base import BaseService
from shared.mixins import AuditableMixin
from software.repositories import ProductoSoftwareRepository, SoftwareInstaladoRepository


class SoftwareInstaladoService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio de instalaciones de software en equipos."""

    ALTA          = 'softwareinstalado.alta'
    BAJA          = 'softwareinstalado.baja'
    ACTUALIZACION = 'softwareinstalado.actualizacion'

    def __init__(self):
        self.repository = SoftwareInstaladoRepository()
        self.producto_repository = ProductoSoftwareRepository()

    def listar(
        self,
        busqueda: str = '',
        equipo_id: int | None = None,
        espacio_id: int | None = None,
        producto_software_id: int | None = None,
    ):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            equipo_id=equipo_id,
            espacio_id=espacio_id,
            producto_software_id=producto_software_id,
        )

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Any = None) -> Any:
        self._validar_unicidad(data)
        self._validar_licencias_disponibles(data)
        instance = self.repository.create(**data, created_by=actor, updated_by=actor)
        return self.repository.get_by_id(instance.id)

    def _do_update(self, id: int, data: dict, actor: Any = None) -> Any:
        instance = self.get_by_id(id)
        data.pop('equipo', None)
        data.pop('producto_software', None)
        data['updated_by'] = actor
        self.repository.update(instance, **data)
        return self.repository.get_by_id(instance.id)

    def _do_delete(self, id: int, actor: Any = None) -> Any:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        self._audit_registrar(instance, self.ALTA, actor, f'{instance} registrado.')

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        if cambios:
            self._audit_registrar(
                instance, self.ACTUALIZACION, actor,
                f'{instance} actualizado.',
                datos_extra={'cambios': cambios},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(instance, self.BAJA, actor, f'{instance} eliminado.')

    def _validar_unicidad(self, data: dict) -> None:
        """Valida que no exista ya una instalacion del producto en el equipo."""
        equipo = data.get('equipo')
        producto_software = data.get('producto_software')
        if not equipo or not producto_software:
            return

        if self.repository.get_by_equipo_producto(equipo.id, producto_software.id):
            raise ValidationError(
                {'detail': 'Este producto de software ya esta instalado en el equipo.'}
            )

    def _validar_licencias_disponibles(self, data: dict) -> None:
        """Impide instalar un producto sin licencias disponibles."""
        producto_software = data.get('producto_software')
        if not producto_software:
            return

        instance = self.producto_repository.get_by_id(producto_software.id)
        if instance and instance.licencias_disponibles <= 0:
            raise ValidationError(
                {'producto_software': 'El producto de software no tiene licencias disponibles.'}
            )
