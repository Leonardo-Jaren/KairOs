from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from equipos.services import EquipoService
from mantenimiento.models import Mantenimiento
from mantenimiento.repositories import MantenimientoRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin
from shared.permissions import get_accessible_space_ids
from shared.constants import ROL_ADMIN, ROL_RESPONSABLE, ROL_SUPERADMIN, ROL_TECNICO
from usuarios.models import Usuario


class MantenimientoService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para gestionar tickets de mantenimiento."""

    APERTURA           = 'mantenimiento.apertura'
    ACTUALIZACION      = 'mantenimiento.actualizacion'
    ASIGNACION_TECNICO = 'mantenimiento.asignacion_tecnico'
    EN_PROCESO         = 'mantenimiento.en_proceso'
    RESOLUCION         = 'mantenimiento.resolucion'
    CANCELACION        = 'mantenimiento.cancelacion'
    RESULTADOS_FINALES = {'en_uso', 'dañado', 'de_baja'}

    OPERATIONAL_ROLES = {ROL_ADMIN, ROL_RESPONSABLE, ROL_TECNICO, ROL_SUPERADMIN}
    VALID_TRANSITIONS = {
        'pendiente': {'en_proceso', 'cancelado'},
        'en_proceso': {'resuelto', 'cancelado'},
    }

    def __init__(self):
        self.repository = MantenimientoRepository()
        self.equipo_service = EquipoService()

    def listar(
        self,
        busqueda: str = '',
        estado: str = '',
        tipo_mantenimiento: str = '',
        equipo_id: int | None = None,
        actor: Usuario = None,
    ):
        _, espacio_ids = self._scope_filters(actor)
        return self.repository.listar(
            busqueda=busqueda.strip(),
            estado=estado.strip(),
            tipo_mantenimiento=tipo_mantenimiento.strip(),
            equipo_id=equipo_id,
            espacio_ids=espacio_ids,
        )

    @transaction.atomic
    def iniciar(self, id: int, actor: Usuario = None) -> Mantenimiento:
        """Inicia la atención de una orden pendiente."""
        instance = self.get_visible_by_id(id, actor)
        if instance.estado != 'pendiente':
            raise ValidationError({
                'estado': 'Solo una orden pendiente puede iniciar atención.'
            })
        return self.update(id, {'estado': 'en_proceso'}, actor=actor)

    @transaction.atomic
    def finalizar(self, id: int, data: dict, actor: Usuario = None) -> dict:
        """Finaliza una orden y aplica el resultado operativo del equipo.

        Cuando la orden correctiva deja el equipo funcional, la incidencia de
        origen se cierra en la misma transacción para evitar estados parciales.
        """
        instance = self.get_visible_by_id(id, actor)
        if instance.estado != 'en_proceso':
            raise ValidationError({
                'estado': 'Solo una orden en atención puede finalizarse.'
            })

        resultado = data.get('resultado_equipo')
        if resultado not in self.RESULTADOS_FINALES:
            raise ValidationError({
                'resultado_equipo': 'Selecciona un resultado final válido.'
            })

        payload = {
            **data,
            'estado': 'resuelto',
            'verificado_por': actor,
            'fecha_verificacion': timezone.now(),
        }
        updated = self.update(id, payload, actor=actor)
        updated.equipo.refresh_from_db()

        incidencia = updated.incidencia_origen
        cerrada_automaticamente = False
        siguiente_accion = None
        if incidencia is not None:
            if updated.resultado_equipo == 'en_uso':
                from incidencias.services import IncidenciaService

                incidencia = IncidenciaService().cerrar_por_mantenimiento(
                    incidencia.id,
                    resolucion=updated.trabajo_realizado,
                    actor=actor,
                )
                cerrada_automaticamente = incidencia.estado == 'cerrado'
            else:
                if incidencia.estado == 'resuelto':
                    from incidencias.services import IncidenciaService

                    incidencia = IncidenciaService().update(
                        incidencia.id,
                        {'estado': 'en_proceso'},
                        actor=actor,
                    )
                siguiente_accion = 'crear_correctivo'
                incidencia.refresh_from_db()

        return {
            'mantenimiento': self.repository.get_by_id(updated.id),
            'equipo': updated.equipo,
            'incidencia': incidencia,
            'cerrada_automaticamente': cerrada_automaticamente,
            'siguiente_accion': siguiente_accion,
        }

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    @transaction.atomic
    def _do_create(self, data: dict, actor: Usuario = None) -> Mantenimiento:
        clean_data = data.copy()
        tecnico_ids = clean_data.pop('tecnicos_ids', [])
        equipo = self._resolver_equipo(clean_data.pop('equipo_id'))
        incidencia = self._resolver_incidencia(
            clean_data.pop('incidencia_id', None),
            equipo,
            clean_data.get('tipo_mantenimiento'),
        )
        self._ensure_can_access_space(equipo.espacio_id, actor)
        reportado_por = self._resolver_reportante(
            clean_data.pop('reportado_por_id', None),
            actor,
        )
        self._validar_tecnicos(tecnico_ids)
        instance = self.repository.create(
            **clean_data,
            equipo=equipo,
            incidencia_origen=incidencia,
            reportado_por=reportado_por,
            created_by=actor,
            updated_by=actor,
        )
        if instance.estado == 'resuelto':
            self._validar_datos_finalizacion(instance)
            instance.verificado_por = actor
            instance.fecha_verificacion = timezone.now()
            instance.save(update_fields=['verificado_por', 'fecha_verificacion', 'updated_at'])
        self.repository.sync_tecnicos(instance, tecnico_ids)
        self._normalizar_fechas(instance, previous_state=None)
        if incidencia is not None and incidencia.estado == 'pendiente':
            self._marcar_incidencia_en_proceso(incidencia.id, actor)
        self._sincronizar_estado_equipo(instance, actor)
        return self.repository.get_by_id(instance.id)

    @transaction.atomic
    def _do_update(self, id: int, data: dict, actor: Usuario = None):
        instance = self.get_visible_by_id(id, actor)
        if instance.estado in {'resuelto', 'cancelado'}:
            raise ValidationError({'estado': 'La orden ya terminó y no admite cambios.'})
        clean_data = data.copy()
        tecnico_ids = clean_data.pop('tecnicos_ids', None)
        previous_state = instance.estado
        if 'equipo_id' in clean_data:
            clean_data['equipo'] = self._resolver_equipo(clean_data.pop('equipo_id'))
        equipo = clean_data.get('equipo', instance.equipo)
        if 'incidencia_id' in clean_data:
            incidencia = self._resolver_incidencia(
                clean_data.pop('incidencia_id'),
                equipo,
                clean_data.get('tipo_mantenimiento', instance.tipo_mantenimiento),
            )
            clean_data['incidencia_origen'] = incidencia
        else:
            incidencia = instance.incidencia_origen
            if incidencia is not None and incidencia.equipo_id != equipo.id:
                raise ValidationError({
                    'equipo_id': 'El equipo debe coincidir con el de la incidencia de origen.'
                })
            if incidencia is not None and clean_data.get(
                'tipo_mantenimiento', instance.tipo_mantenimiento
            ) != 'correctivo':
                raise ValidationError({
                    'tipo_mantenimiento': 'Un mantenimiento con incidencia de origen debe ser correctivo.'
                })
        self._ensure_can_access_space(equipo.espacio_id, actor)
        target_state = clean_data.get('estado', instance.estado)
        self._validar_transicion(previous_state, target_state)
        if target_state == 'resuelto':
            candidate = instance.__class__(
                diagnostico=clean_data.get('diagnostico', instance.diagnostico),
                trabajo_realizado=clean_data.get('trabajo_realizado', instance.trabajo_realizado),
                resultado_equipo=clean_data.get('resultado_equipo', instance.resultado_equipo),
                prueba_realizada=clean_data.get('prueba_realizada', instance.prueba_realizada),
            )
            self._validar_datos_finalizacion(candidate)
            clean_data['verificado_por'] = actor
            clean_data['fecha_verificacion'] = timezone.now()
        if 'reportado_por_id' in clean_data:
            clean_data['reportado_por'] = self._resolver_reportante(
                clean_data.pop('reportado_por_id'),
                actor,
            )
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        self._normalizar_fechas(instance, previous_state=previous_state)
        tecnicos_cambiaron = False
        if tecnico_ids is not None:
            self._validar_tecnicos(tecnico_ids)
            self.repository.sync_tecnicos(instance, tecnico_ids)
            tecnicos_cambiaron = True
        updated = self.repository.get_by_id(instance.id)
        self._sincronizar_estado_equipo(updated, actor)
        return updated, {'tecnicos_cambiaron': tecnicos_cambiaron}

    def _do_delete(self, id: int, actor: Usuario = None) -> Mantenimiento:
        instance = self.get_visible_by_id(id, actor)
        self.repository.soft_delete(instance, actor)
        self._sincronizar_estado_equipo(instance, actor)
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

    def get_estadisticas(self, actor: Usuario = None) -> dict:
        """Retorna indicadores agregados para la cabecera del modulo."""
        _, espacio_ids = self._scope_filters(actor)
        stats = self.repository.get_estadisticas()
        if espacio_ids is None:
            return stats
        scoped = self.repository.listar(espacio_ids=espacio_ids)
        from django.db.models import Count, Q
        return {
            **scoped.aggregate(
                total=Count('id'),
                pendientes=Count('id', filter=Q(estado='pendiente')),
                en_proceso=Count('id', filter=Q(estado='en_proceso')),
                resueltos=Count('id', filter=Q(estado='resuelto')),
                cancelados=Count('id', filter=Q(estado='cancelado')),
            ),
            'total_tecnicos': stats['total_tecnicos'],
            'total_dispositivos': stats['total_dispositivos'],
        }

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

    def _resolver_incidencia(self, incidencia_id, equipo, tipo_mantenimiento):
        if incidencia_id is None:
            return None
        if tipo_mantenimiento != 'correctivo':
            raise ValidationError({'incidencia_id': 'Solo un mantenimiento correctivo puede originarse en una incidencia.'})
        incidencia = self.repository.get_incidencia_by_id(incidencia_id)
        if incidencia is None:
            raise ValidationError({'incidencia_id': 'La incidencia no existe o fue retirada.'})
        if incidencia.equipo_id != equipo.id:
            raise ValidationError({'incidencia_id': 'La incidencia y el equipo deben coincidir.'})
        if incidencia.estado in {'cerrado', 'cancelado', 'duplicado'}:
            raise ValidationError({'incidencia_id': 'La incidencia ya no admite nuevas órdenes.'})
        return incidencia

    def _resolver_reportante(
        self,
        reportado_por_id: int | None,
        actor: Usuario | None,
    ) -> Usuario:
        """Resuelve un reportante activo o usa al actor autenticado por defecto."""
        usuario_id = (
            reportado_por_id
            if reportado_por_id is not None
            else getattr(actor, 'id', None)
        )
        reportante = self.repository.get_usuario_activo_by_id(usuario_id)
        if reportante is None:
            raise ValidationError({
                'reportado_por_id': 'El usuario reportante no existe o está inactivo.'
            })
        return reportante

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

    def get_visible_by_id(self, id: int, actor: Usuario = None):
        instance = self.get_by_id(id)
        self._ensure_can_access_space(instance.equipo.espacio_id, actor)
        return instance

    def _validar_transicion(self, actual: str, nuevo: str) -> None:
        if nuevo == actual:
            return
        if nuevo not in self.VALID_TRANSITIONS.get(actual, set()):
            raise ValidationError({
                'estado': f'No se puede cambiar de "{actual}" a "{nuevo}".'
            })

    def _normalizar_fechas(self, instance, previous_state=None) -> None:
        """Sincroniza fechas de atención después de persistir la orden."""
        updates = {}
        if instance.estado in {'en_proceso', 'resuelto', 'cancelado'} and instance.fecha_inicio is None:
            updates['fecha_inicio'] = timezone.now()
        if instance.estado in {'resuelto', 'cancelado'} and instance.fecha_fin is None:
            updates['fecha_fin'] = timezone.now()
        if updates:
            self.repository.update(instance, **updates)

    def _validar_datos_finalizacion(self, instance: Mantenimiento) -> None:
        """Valida los datos necesarios para finalizar una orden."""
        if not instance.diagnostico.strip():
            raise ValidationError({'diagnostico': 'El diagnóstico es obligatorio al finalizar.'})
        if not instance.trabajo_realizado.strip():
            raise ValidationError({'trabajo_realizado': 'Describe el trabajo realizado al finalizar.'})
        if not instance.prueba_realizada:
            raise ValidationError({
                'prueba_realizada': 'Confirma que se realizó la prueba de funcionamiento.'
            })
        if instance.resultado_equipo not in self.RESULTADOS_FINALES:
            raise ValidationError({
                'resultado_equipo': 'Selecciona un resultado final válido.'
            })

    def _sincronizar_estado_equipo(self, instance, actor) -> None:
        if instance.is_deleted:
            target = instance.resultado_equipo or 'en_uso'
            if self.repository.has_active_for_equipo(instance.equipo_id, exclude_id=instance.id):
                target = 'en_mantenimiento'
        elif instance.estado == 'en_proceso':
            target = 'en_mantenimiento'
        elif instance.estado in {'resuelto', 'cancelado'}:
            target = instance.resultado_equipo or 'en_uso'
            if self.repository.has_active_for_equipo(instance.equipo_id, exclude_id=instance.id):
                target = 'en_mantenimiento'
        else:
            return
        if instance.equipo.estado != target:
            self.equipo_service.update(instance.equipo_id, {'estado': target}, actor=actor)

    def _marcar_incidencia_en_proceso(self, incidencia_id: int, actor: Usuario) -> None:
        from incidencias.services import IncidenciaService

        IncidenciaService().update(incidencia_id, {'estado': 'en_proceso'}, actor=actor)

    def _scope_filters(self, actor: Usuario):
        if actor and (actor.rol in self.OPERATIONAL_ROLES or actor.is_superuser):
            return None, get_accessible_space_ids(actor)
        return None, set()

    def _ensure_can_access_space(self, espacio_id: int | None, actor: Usuario) -> None:
        if actor is None:
            return
        if actor.rol in {ROL_ADMIN, ROL_SUPERADMIN} or actor.is_superuser:
            return
        espacio_ids = get_accessible_space_ids(actor)
        if espacio_id is None or espacio_ids is not None and espacio_id not in espacio_ids:
            raise PermissionDenied('No tienes alcance operativo sobre este espacio.')
