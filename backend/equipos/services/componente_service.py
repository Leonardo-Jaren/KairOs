from rest_framework.exceptions import ValidationError

from equipos.models import Componente
from equipos.repositories import ComponenteRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario


class ComponenteService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para gestionar componentes de equipos."""

    COMPONENTE_AGREGADO   = 'equipo.componente_agregado'
    COMPONENTE_MODIFICADO = 'equipo.componente_modificado'
    COMPONENTE_ELIMINADO  = 'equipo.componente_eliminado'

    def __init__(self):
        self.repository = ComponenteRepository()

    def listar(
        self,
        equipo_id: int | None = None,
        busqueda: str = '',
        tipo: str = '',
    ):
        """Lista componentes aplicando los filtros solicitados por la interfaz."""
        return self.repository.listar(
            equipo_id=equipo_id,
            busqueda=busqueda,
            tipo=tipo,
        )

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Usuario = None):
        clean_data = data.copy()
        equipo = self._resolver_equipo(clean_data.pop('equipo_id'))
        instance = self.repository.create(
            **clean_data,
            equipo=equipo,
            created_by=actor,
            updated_by=actor,
        )
        return self.repository.get_by_id(instance.id), {'equipo': equipo}

    def _do_update(self, id: int, data: dict, actor: Usuario = None) -> Componente:
        instance = self.get_by_id(id)
        clean_data = data.copy()
        clean_data.pop('equipo_id', None)
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def _do_delete(self, id: int, actor: Usuario = None) -> Componente:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría — registra sobre el Equipo padre ───────────────────
    # Los eventos se asocian al equipo para que aparezcan en su línea de tiempo.

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        equipo = ctx['equipo']
        self._audit_registrar(
            equipo, self.COMPONENTE_AGREGADO, actor,
            f'Componente {instance.get_tipo_display()} ({instance.modelo}) agregado a {equipo.codigo}.',
            datos_extra={'componente_id': instance.id, 'tipo': instance.tipo, 'modelo': instance.modelo},
        )

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        if cambios:
            self._audit_registrar(
                instance.equipo, self.COMPONENTE_MODIFICADO, actor,
                f'Componente {instance.get_tipo_display()} de {instance.equipo.codigo} modificado.',
                datos_extra={'componente_id': instance.id, 'cambios': cambios},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(
            instance.equipo, self.COMPONENTE_ELIMINADO, actor,
            f'Componente {instance.get_tipo_display()} ({instance.modelo}) eliminado de {instance.equipo.codigo}.',
            datos_extra={'componente_id': instance.id, 'tipo': instance.tipo},
        )

    # ── Auxiliares ─────────────────────────────────────────────────────────────

    def _resolver_equipo(self, equipo_id: int):
        equipo = self.repository.get_equipo_by_id(equipo_id)
        if equipo is None:
            raise ValidationError({'equipo_id': 'El equipo no existe o fue dado de baja.'})
        return equipo
