from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from incidencias.repositories import IncidenciaRepository
from shared.base import BaseService
from shared.constants import (
    ROL_ADMIN,
    ROL_DOCENTE,
    ROL_RESPONSABLE,
    ROL_SUPERADMIN,
    ROL_TECNICO,
    ROL_USUARIO,
)
from shared.mixins import AuditableMixin
from shared.permissions import get_accessible_space_ids


class IncidenciaService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para gestionar incidencias."""

    ALTA          = 'incidencia.alta'
    BAJA          = 'incidencia.baja'
    ACTUALIZACION = 'incidencia.actualizacion'
    CAMBIO_ESTADO = 'incidencia.cambio_estado'
    CIERRE_MANTENIMIENTO = 'incidencia.cierre_por_mantenimiento'

    REPORTER_ROLES = {ROL_DOCENTE, ROL_USUARIO}
    OPERATIONAL_ROLES = {ROL_ADMIN, ROL_RESPONSABLE, ROL_TECNICO, ROL_SUPERADMIN}
    TERMINAL_STATES = {'cerrado', 'cancelado', 'duplicado'}
    VALID_TRANSITIONS = {
        'pendiente': {'en_proceso', 'cancelado', 'duplicado'},
        'en_proceso': {'resuelto', 'cancelado', 'duplicado'},
        'resuelto': {'cerrado', 'en_proceso'},
    }

    def __init__(self):
        self.repository = IncidenciaRepository()

    def listar(
        self,
        busqueda: str = '',
        espacio_id: int | None = None,
        equipo_id: int | None = None,
        tipo_incidencia: str = '',
        estado: str = '',
        prioridad: str = '',
        asignado_a_id: int | None = None,
        actor: Any = None,
    ):
        reportado_por_id, espacio_ids = self._scope_filters(actor)
        return self.repository.listar(
            busqueda=busqueda.strip(),
            espacio_id=espacio_id,
            equipo_id=equipo_id,
            tipo_incidencia=tipo_incidencia.strip(),
            estado=estado.strip(),
            prioridad=prioridad.strip(),
            asignado_a_id=asignado_a_id,
            reportado_por_id=reportado_por_id,
            espacio_ids=espacio_ids,
        )

    def get_visible_by_id(self, id: int, actor: Any = None) -> Any:
        """Obtiene una incidencia validando autoría y alcance territorial."""
        instance = self.get_by_id(id)
        self._ensure_visible(instance, actor)
        return instance

    def get_mantenimientos(self, id: int, actor: Any = None):
        """Retorna las órdenes asociadas después de validar visibilidad."""
        instance = self.get_visible_by_id(id, actor)
        return instance.mantenimientos.filter(is_deleted=False).select_related(
            'equipo', 'reportado_por'
        ).prefetch_related('tecnicos_asignados__tecnico__usuario')

    @transaction.atomic
    def cerrar_por_mantenimiento(
        self,
        id: int,
        resolucion: str,
        actor: Any = None,
    ) -> Any:
        """Cierra una incidencia tras verificar un correctivo funcional."""
        instance = self.get_visible_by_id(id, actor)
        if instance.estado == 'cerrado':
            return instance
        if instance.estado in {'cancelado', 'duplicado'}:
            raise ValidationError({
                'estado': 'La incidencia terminal no puede cerrarse por mantenimiento.'
            })

        resolucion = (resolucion or '').strip()
        if not resolucion:
            raise ValidationError({
                'resolucion': 'El trabajo realizado es necesario para cerrar la incidencia.'
            })

        if instance.estado == 'pendiente':
            instance = self.update(
                id,
                {'estado': 'en_proceso'},
                actor=actor,
            )
        if instance.estado == 'en_proceso':
            instance = self.update(
                id,
                {'estado': 'resuelto', 'resolucion': resolucion},
                actor=actor,
            )
        instance = self.update(
            id,
            {'estado': 'cerrado', 'resolucion': resolucion},
            actor=actor,
        )
        self._audit_registrar(
            instance,
            self.CIERRE_MANTENIMIENTO,
            actor,
            f'{instance} cerrada automáticamente tras finalizar el mantenimiento.',
        )
        return instance

    def get_tecnicos_disponibles(self):
        """Retorna técnicos activos para el panel de triage."""
        return self.repository.get_tecnicos_disponibles()

    def puede_operar(self, actor: Any) -> bool:
        """Indica si el actor puede intervenir sobre una incidencia."""
        return bool(
            actor
            and actor.is_authenticated
            and (actor.is_superuser or actor.rol in self.OPERATIONAL_ROLES)
        )

    def _ensure_visible(self, instance, actor: Any = None) -> None:
        if actor is None:
            return
        if actor.rol in self.REPORTER_ROLES:
            if instance.created_by_id != actor.id:
                raise self._not_found_error(instance.id)
            return
        if actor.rol not in self.OPERATIONAL_ROLES and not actor.is_superuser:
            raise self._not_found_error(instance.id)
        espacio_ids = get_accessible_space_ids(actor)
        if espacio_ids is not None and instance.espacio_id not in espacio_ids:
            raise self._not_found_error(instance.id)

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    @transaction.atomic
    def _do_create(self, data: dict, actor: Any = None) -> Any:
        clean_data = data.copy()
        espacio = clean_data.get('espacio')
        equipo = clean_data.get('equipo')
        self._validar_equipo_espacio(equipo, espacio)
        self._ensure_can_access_space(espacio.id, actor)
        # El ciclo siempre comienza en pendiente; el soporte cambia el estado.
        for field in ('estado', 'fecha_resolucion', 'resolucion', 'motivo_cierre', 'asignado_a'):
            clean_data.pop(field, None)
        clean_data['estado'] = 'pendiente'
        clean_data['fecha_resolucion'] = None
        clean_data['resolucion'] = ''
        clean_data['motivo_cierre'] = ''
        instance = self.repository.create(
            **clean_data,
            created_by=actor,
            updated_by=actor,
        )
        return self.repository.get_by_id(instance.id)

    @transaction.atomic
    def _do_update(self, id: int, data: dict, actor: Any = None) -> Any:
        instance = self.get_visible_by_id(id, actor)
        if not self.puede_operar(actor):
            raise PermissionDenied('Solo el personal operativo puede actualizar incidencias.')
        if instance.estado in self.TERMINAL_STATES:
            raise ValidationError({'estado': 'La incidencia ya está cerrada y no admite cambios.'})

        clean_data = data.copy()
        target_state = clean_data.get('estado', instance.estado)
        self._validar_transicion(instance.estado, target_state)

        equipo = clean_data.get('equipo', instance.equipo)
        espacio = clean_data.get('espacio', instance.espacio)
        self._validar_equipo_espacio(equipo, espacio)
        self._ensure_can_access_space(espacio.id, actor)
        if 'asignado_a' in clean_data and clean_data['asignado_a'] is not None:
            if self.repository.get_tecnico_by_id(clean_data['asignado_a'].id) is None:
                raise ValidationError({'asignado_a': 'El técnico no existe o está inactivo.'})

        resolucion = clean_data.get('resolucion', instance.resolucion).strip()
        motivo_cierre = clean_data.get('motivo_cierre', instance.motivo_cierre).strip()
        if target_state in {'resuelto', 'cerrado'} and not resolucion:
            raise ValidationError({'resolucion': 'La resolución es obligatoria para resolver o cerrar.'})
        if target_state in {'cancelado', 'duplicado'} and not motivo_cierre:
            raise ValidationError({'motivo_cierre': 'Indica por qué se cerró la incidencia.'})

        clean_data['resolucion'] = resolucion
        clean_data['motivo_cierre'] = motivo_cierre
        clean_data = self._normalizar_estado(clean_data, instance)
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
        reportado_por_id, espacio_ids = self._scope_filters(actor)
        return self.repository.get_estadisticas(
            reportado_por_id=reportado_por_id,
            espacio_ids=espacio_ids,
        )

    def get_espacios_opciones(self, actor: Any = None):
        """Espacios disponibles para el formulario de incidencias."""
        _, espacio_ids = self._scope_filters(actor)
        return self.repository.get_espacios_opciones(espacio_ids=espacio_ids)

    def get_equipos_opciones(self, espacio_id: int | None = None, actor: Any = None):
        """Equipos disponibles para el formulario de incidencias."""
        _, espacio_ids = self._scope_filters(actor)
        return self.repository.get_equipos_opciones(
            espacio_id=espacio_id,
            espacio_ids=espacio_ids,
        )

    def _normalizar_estado(self, data: dict, instance=None) -> dict:
        """Sincroniza fecha_resolucion con el estado de la incidencia."""
        clean_data = data.copy()
        if 'estado' in clean_data:
            if clean_data['estado'] == 'resuelto':
                clean_data['fecha_resolucion'] = timezone.now()
            elif clean_data['estado'] == 'cerrado' and instance is not None:
                clean_data['fecha_resolucion'] = instance.fecha_resolucion or timezone.now()
            elif clean_data['estado'] not in {'resuelto', 'cerrado'}:
                clean_data['fecha_resolucion'] = None
        return clean_data

    def _validar_equipo_espacio(self, equipo, espacio) -> None:
        if equipo is None or espacio is None:
            raise ValidationError({'equipo': 'El equipo y el espacio son obligatorios.'})
        if equipo.is_deleted or equipo.espacio_id != espacio.id:
            raise ValidationError({
                'equipo': 'El equipo no pertenece al espacio seleccionado o fue retirado.'
            })

    def _validar_transicion(self, actual: str, nuevo: str) -> None:
        if nuevo == actual:
            return
        permitidos = self.VALID_TRANSITIONS.get(actual, set())
        if nuevo not in permitidos:
            raise ValidationError({
                'estado': f'No se puede cambiar de "{actual}" a "{nuevo}".'
            })

    def _ensure_can_access_space(self, espacio_id: int, actor: Any) -> None:
        if actor is None or actor.rol in self.REPORTER_ROLES:
            return
        espacio_ids = get_accessible_space_ids(actor)
        if espacio_ids is not None and espacio_id not in espacio_ids:
            raise PermissionDenied('No tienes alcance operativo sobre este espacio.')

    def _scope_filters(self, actor: Any):
        if actor and actor.rol in self.REPORTER_ROLES:
            return actor.id, None
        if actor and (actor.rol in self.OPERATIONAL_ROLES or actor.is_superuser):
            return None, get_accessible_space_ids(actor)
        return None, set()
