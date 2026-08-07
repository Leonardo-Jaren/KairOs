from rest_framework.exceptions import ValidationError

from mantenimiento.models import Mantenimiento
from mantenimiento.repositories import MantenimientoRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario


class MantenimientoService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para gestionar tickets de mantenimiento."""

    APERTURA           = 'mantenimiento.apertura'
    ACTUALIZACION      = 'mantenimiento.actualizacion'
    ASIGNACION_TECNICO = 'mantenimiento.asignacion_tecnico'
    EN_PROCESO         = 'mantenimiento.en_proceso'
    RESOLUCION         = 'mantenimiento.resolucion'
    CANCELACION        = 'mantenimiento.cancelacion'

    def __init__(self):
        self.repository = MantenimientoRepository()

    def listar(
        self,
        busqueda: str = '',
        estado: str = '',
        tipo_mantenimiento: str = '',
        equipo_id: int | None = None,
    ):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            estado=estado.strip(),
            tipo_mantenimiento=tipo_mantenimiento.strip(),
            equipo_id=equipo_id,
        )

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Usuario = None) -> Mantenimiento:
        clean_data = data.copy()
        tecnico_ids = clean_data.pop('tecnicos_ids', [])
        equipo = self._resolver_equipo(clean_data.pop('equipo_id'))
        self._validar_tecnicos(tecnico_ids)
        instance = self.repository.create(**clean_data, equipo=equipo, created_by=actor, updated_by=actor)
        self.repository.sync_tecnicos(instance, tecnico_ids)
        return self.repository.get_by_id(instance.id)

    def _do_update(self, id: int, data: dict, actor: Usuario = None):
        instance = self.get_by_id(id)
        clean_data = data.copy()
        tecnico_ids = clean_data.pop('tecnicos_ids', None)
        if 'equipo_id' in clean_data:
            clean_data['equipo'] = self._resolver_equipo(clean_data.pop('equipo_id'))
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        tecnicos_cambiaron = False
        if tecnico_ids is not None:
            self._validar_tecnicos(tecnico_ids)
            self.repository.sync_tecnicos(instance, tecnico_ids)
            tecnicos_cambiaron = True
        return self.repository.get_by_id(instance.id), {'tecnicos_cambiaron': tecnicos_cambiaron}

    def _do_delete(self, id: int, actor: Usuario = None) -> Mantenimiento:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        self._audit_registrar(instance, self.APERTURA, actor, f'Ticket {instance} abierto.')

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        ctx = ctx or {}
        restantes = []
        for cambio in cambios:
            if cambio['campo'] == 'Estado':
                nuevo = cambio['despues']
                if nuevo == 'en_proceso':
                    self._audit_registrar(instance, self.EN_PROCESO, actor,
                        f'Ticket {instance}: trabajo iniciado.')
                elif nuevo == 'resuelto':
                    self._audit_registrar(instance, self.RESOLUCION, actor,
                        f'Ticket {instance} resuelto.')
                elif nuevo == 'cancelado':
                    self._audit_registrar(instance, self.CANCELACION, actor,
                        f'Ticket {instance} cancelado.')
            else:
                restantes.append(cambio)
        if ctx.get('tecnicos_cambiaron'):
            self._audit_registrar(instance, self.ASIGNACION_TECNICO, actor,
                f'Técnicos del ticket {instance} actualizados.')
        if restantes:
            self._audit_registrar(instance, self.ACTUALIZACION, actor,
                f'Ticket {instance} actualizado.',
                datos_extra={'cambios': restantes},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(instance, self.CANCELACION, actor, f'Ticket {instance} cancelado.')

    def get_estadisticas(self) -> dict:
        """Retorna indicadores agregados para la cabecera del modulo."""
        return self.repository.get_estadisticas()

    def get_tecnicos_disponibles(self):
        """Retorna tecnicos vigentes disponibles para asignar a un ticket."""
        return self.repository.get_tecnicos_disponibles()

    def _resolver_equipo(self, equipo_id: int):
        """Resuelve el equipo asociado reportando si no existe o fue retirado."""
        equipo = self.repository.get_equipo_by_id(equipo_id)
        if equipo is None:
            raise ValidationError({
                'equipo_id': 'El equipo no existe o fue retirado.'
            })
        return equipo

    def _validar_tecnicos(self, tecnico_ids: list[int]) -> None:
        """Valida que los tecnicos elegidos existan y esten vigentes."""
        if not tecnico_ids:
            return
        encontrados = set(
            self.repository.get_tecnicos_por_ids(tecnico_ids).values_list('id', flat=True)
        )
        faltantes = set(tecnico_ids) - encontrados
        if faltantes:
            raise ValidationError({
                'tecnicos_ids': f'Los siguientes tecnicos no existen o no estan vigentes: {sorted(faltantes)}'
            })
