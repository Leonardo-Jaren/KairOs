from typing import Any

from django.utils import timezone

from incidencias.repositories import IncidenciaRepository
from shared.base import BaseService
from shared.constants import ROL_DOCENTE
from shared.mixins import AuditableMixin


class IncidenciaService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para gestionar incidencias."""

    ALTA          = 'incidencia.alta'
    BAJA          = 'incidencia.baja'
    ACTUALIZACION = 'incidencia.actualizacion'
    CAMBIO_ESTADO = 'incidencia.cambio_estado'

    def __init__(self):
        self.repository = IncidenciaRepository()

    def listar(
        self,
        busqueda: str = '',
        espacio_id: int | None = None,
        equipo_id: int | None = None,
        tipo_incidencia: str = '',
        estado: str = '',
        actor: Any = None,
    ):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            espacio_id=espacio_id,
            equipo_id=equipo_id,
            tipo_incidencia=tipo_incidencia.strip(),
            estado=estado.strip(),
            reportado_por_id=self._alcance_reportante(actor),
        )

    def get_visible_by_id(self, id: int, actor: Any = None) -> Any:
        """Obtiene una incidencia validando que el docente solo vea las suyas."""
        instance = self.get_by_id(id)
        if actor and actor.rol == ROL_DOCENTE and instance.created_by_id != actor.id:
            raise self._not_found_error(id)
        return instance

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Any = None) -> Any:
        instance = self.repository.create(**data, created_by=actor, updated_by=actor)
        return self.repository.get_by_id(instance.id)

    def _do_update(self, id: int, data: dict, actor: Any = None) -> Any:
        instance = self.get_by_id(id)
        clean_data = self._normalizar_estado(data)
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def _do_delete(self, id: int, actor: Any = None) -> Any:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        self._audit_registrar(instance, self.ALTA, actor, f'{instance} registrada.')

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        restantes = []
        for cambio in cambios:
            if cambio['campo'] == 'Estado':
                self._audit_registrar(
                    instance, self.CAMBIO_ESTADO, actor,
                    f'{instance}: estado cambió a "{cambio["despues"]}".',
                    datos_extra={'cambios': [cambio]},
                )
            else:
                restantes.append(cambio)
        if restantes:
            self._audit_registrar(
                instance, self.ACTUALIZACION, actor,
                f'{instance} actualizada.',
                datos_extra={'cambios': restantes},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(instance, self.BAJA, actor, f'{instance} eliminada.')

    def get_estadisticas(self, actor: Any = None) -> dict:
        """Retorna indicadores para la cabecera del modulo."""
        return self.repository.get_estadisticas(reportado_por_id=self._alcance_reportante(actor))

    def get_espacios_opciones(self):
        """Espacios disponibles para el formulario de incidencias."""
        return self.repository.get_espacios_opciones()

    def get_equipos_opciones(self, espacio_id: int | None = None):
        """Equipos disponibles para el formulario de incidencias."""
        return self.repository.get_equipos_opciones(espacio_id=espacio_id)

    def _normalizar_estado(self, data: dict) -> dict:
        """Sincroniza fecha_resolucion con el estado de la incidencia."""
        clean_data = data.copy()
        if 'estado' in clean_data:
            clean_data['fecha_resolucion'] = (
                timezone.localdate() if clean_data['estado'] == 'resuelto' else None
            )
        return clean_data

    def _alcance_reportante(self, actor: Any) -> int | None:
        """Restringe la consulta al propio autor cuando el rol es docente."""
        if actor and actor.rol == ROL_DOCENTE:
            return actor.id
        return None
