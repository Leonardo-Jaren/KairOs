from django.db import IntegrityError, transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from espacios.models import Edificio, Espacio, EspacioUsuario, Local
from espacios.repositories import EspacioUsuarioRepository
from shared.base import BaseService
from shared.constants import (
    ROL_ADMIN,
    ROL_RESPONSABLE,
    ROL_SUPERADMIN,
    ROL_TECNICO,
    ROL_DOCENTE,
)
from shared.mixins import AuditableMixin
from usuarios.models import Usuario


class EspacioUsuarioService(AuditableMixin, BaseService):
    """Aplica reglas para asignar usuarios a ámbitos territoriales físicos."""

    ASIGNACION_USUARIO = 'espacio.asignacion_usuario'
    ACTUALIZACION      = 'espacio.actualizacion_asignacion'
    RETIRO_USUARIO     = 'espacio.retiro_usuario'

    def __init__(self):
        self.repository = EspacioUsuarioRepository()

    def listar(
        self,
        busqueda: str = '',
        activo: bool | None = None,
        usuario_id: int | None = None,
        espacio_id: int | None = None,
        ambito: str | None = None,
        local_id: int | None = None,
        edificio_id: int | None = None,
        piso: str | None = None,
        sede_ids: list[int] | None = None,
        ordering: str | None = None,
    ):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            activo=activo,
            usuario_id=usuario_id,
            espacio_id=espacio_id,
            ambito=ambito,
            local_id=local_id,
            edificio_id=edificio_id,
            piso=piso,
            sede_ids=sede_ids,
            ordering=ordering,
        )

    # ── Validación de Permisos por Sede ────────────────────────────────────────

    def validar_permiso_sede(self, actor: Usuario | None, local_id: int | None) -> None:
        """
        Verifica que el actor tenga autorización para operar en la sede target.
        - Superadmin y Admin tienen acceso global universal.
        - Responsable solo puede operar en sedes físicas activas asignadas a su cuenta (UsuarioSede).
        - Si la sede no está autorizada, levanta PermissionDenied (HTTP 403 Forbidden).
        - Técnicos, docentes y usuarios estándar carecen de permisos de mutación.
        """
        if not actor or not actor.is_authenticated:
            return

        if actor.rol in (ROL_SUPERADMIN, ROL_ADMIN) or actor.is_superuser:
            return

        if actor.rol == ROL_RESPONSABLE:
            sedes_responsable = set(
                actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True)
            )
            if local_id is None or local_id not in sedes_responsable:
                raise PermissionDenied('No tienes autorización para gestionar asignaciones en una sede ajena.')
            return

        raise PermissionDenied('No tienes permisos para gestionar asignaciones territoriales.')

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Usuario = None):
        clean_data = data.copy()
        relaciones = self._resolver_relaciones(clean_data)

        usuario = relaciones['usuario']
        ambito = relaciones['ambito']
        local = relaciones['local']
        edificio = relaciones['edificio']
        piso = relaciones['piso']
        espacio = relaciones['espacio']
        tipo = clean_data.get('tipo_responsabilidad', 'responsable')

        # Control estricto de autorización por sede (HTTP 403)
        if actor:
            self.validar_permiso_sede(actor, local.id if local else None)

        ctx = {
            'usuario': usuario,
            'ambito': ambito,
            'local': local,
            'edificio': edificio,
            'piso': piso,
            'espacio': espacio,
            'tipo': tipo,
        }

        # Búsqueda de asignación previa (activa o soft-deleted) en el mismo ámbito
        existing = self.repository.get_by_scope(
            ambito=ambito,
            usuario_id=usuario.id,
            local_id=local.id if local else None,
            edificio_id=edificio.id if edificio else None,
            piso=piso,
            espacio_id=espacio.id if espacio else None,
        )

        try:
            with transaction.atomic():
                if existing and existing.is_deleted:
                    instance = self.repository.restore(
                        instance=existing,
                        tipo_responsabilidad=tipo,
                        actor=actor,
                        ambito=ambito,
                        local=local,
                        edificio=edificio,
                        piso=piso,
                        espacio=espacio,
                    )
                    if instance.activo and not instance.is_deleted:
                        self._auto_asociar_supervisor_sede(usuario, local or instance.local)
                    return instance, {**ctx, 'restored': True}

                # Verificación de unicidad para asignaciones activas vigentes
                self._validar_unicidad(
                    ambito=ambito,
                    usuario_id=usuario.id,
                    local_id=local.id if local else None,
                    edificio_id=edificio.id if edificio else None,
                    piso=piso,
                    espacio_id=espacio.id if espacio else None,
                )

                instance = self.repository.create(
                    ambito=ambito,
                    usuario=usuario,
                    local=local,
                    edificio=edificio,
                    piso=piso,
                    espacio=espacio,
                    tipo_responsabilidad=tipo,
                    activo=clean_data.get('activo', True),
                    created_by=actor,
                    updated_by=actor,
                )
                if instance.activo and not instance.is_deleted:
                    self._auto_asociar_supervisor_sede(usuario, local or instance.local)
                return instance, {**ctx, 'restored': False}
        except IntegrityError:
            raise ValidationError({'detail': 'El usuario ya está asignado a este ámbito.'})

    def _do_update(self, id: int, data: dict, actor: Usuario = None) -> EspacioUsuario:
        instance = self.get_by_id(id)

        # Verificar permiso sobre la sede actual antes de modificar
        if actor:
            self.validar_permiso_sede(actor, instance.local_id)

        clean_data = data.copy()
        ambito = clean_data.get('ambito', instance.ambito)
        usuario_id = clean_data.get('usuario_id', instance.usuario_id)
        local_id = clean_data.get('local_id', instance.local_id)
        edificio_id = clean_data.get('edificio_id', instance.edificio_id)
        piso = clean_data.get('piso', instance.piso)
        espacio_id = clean_data.get('espacio_id', instance.espacio_id)

        relaciones = self._resolver_relaciones({
            'ambito': ambito,
            'usuario_id': usuario_id,
            'local_id': local_id,
            'edificio_id': edificio_id,
            'piso': piso,
            'espacio_id': espacio_id,
        })

        # Verificar permiso sobre la sede destino si cambió
        if actor and relaciones['local']:
            self.validar_permiso_sede(actor, relaciones['local'].id)

        self._validar_unicidad(
            ambito=relaciones['ambito'],
            usuario_id=relaciones['usuario'].id,
            local_id=relaciones['local'].id if relaciones['local'] else None,
            edificio_id=relaciones['edificio'].id if relaciones['edificio'] else None,
            piso=relaciones['piso'],
            espacio_id=relaciones['espacio'].id if relaciones['espacio'] else None,
            exclude_id=instance.id,
        )

        clean_data.update({
            'ambito': relaciones['ambito'],
            'usuario': relaciones['usuario'],
            'local': relaciones['local'],
            'edificio': relaciones['edificio'],
            'piso': relaciones['piso'],
            'espacio': relaciones['espacio'],
            'updated_by': actor,
        })
        clean_data.pop('usuario_id', None)
        clean_data.pop('local_id', None)
        clean_data.pop('edificio_id', None)
        clean_data.pop('espacio_id', None)

        try:
            with transaction.atomic():
                updated_instance = self.repository.update(instance, **clean_data)
                target_local = relaciones.get('local') or updated_instance.local
                target_usuario = relaciones.get('usuario') or updated_instance.usuario
                if updated_instance.activo and not updated_instance.is_deleted:
                    self._auto_asociar_supervisor_sede(target_usuario, target_local)
                return updated_instance
        except IntegrityError:
            raise ValidationError({'detail': 'El usuario ya está asignado a este ámbito.'})

    def _auto_asociar_supervisor_sede(
        self,
        usuario: Usuario | None,
        local: Local | None,
    ) -> None:
        """
        Auto-asocia al responsable activo de la sede física como supervisor directo
        del técnico asignado, si este último no cuenta con un supervisor previo (F5 y F6).

        Reglas aplicadas:
        - Exclusivo para usuarios con rol 'tecnico'.
        - Preserva intacto el supervisor previo si usuario.supervisor_id no es None (F6).
        - Excluye docentes y otros roles institucionales.
        - Si la sede carece de responsable activo, supervisor permanece None sin error.
        - Prioriza desempate por sede principal (-es_sede_principal) y antigüedad.
        """
        if not usuario or usuario.rol != ROL_TECNICO or usuario.supervisor_id is not None:
            return

        if not local:
            return

        from usuarios.models import UsuarioSede

        responsable_asig = (
            UsuarioSede.objects.filter(
                local=local,
                usuario__rol=ROL_RESPONSABLE,
                usuario__is_active=True,
                activo=True,
                is_deleted=False,
            )
            .select_related('usuario')
            .order_by('-es_sede_principal', 'created_at', 'id')
            .first()
        )

        if responsable_asig and responsable_asig.usuario:
            if responsable_asig.usuario_id != usuario.id:
                usuario.supervisor = responsable_asig.usuario
                usuario.save(update_fields=['supervisor'])

    def _do_delete(self, id: int, actor: Usuario = None) -> EspacioUsuario:
        instance = self.get_by_id(id)
        if actor:
            self.validar_permiso_sede(actor, instance.local_id)
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _describir_ambito(self, instance: EspacioUsuario) -> str:
        """Construye una descripción legible y segura del ámbito asignado."""
        if instance.espacio:
            return instance.espacio.codigo_espacio
        if instance.ambito == EspacioUsuario.AMBITO_SEDE:
            return f'Sede {instance.local.nombre if instance.local else ""}'.strip()
        if instance.ambito == EspacioUsuario.AMBITO_EDIFICIO:
            return f'Edificio {instance.edificio.nombre if instance.edificio else ""}'.strip()
        if instance.ambito == EspacioUsuario.AMBITO_PISO:
            edif = instance.edificio.nombre if instance.edificio else "Edificio"
            return f'Piso {instance.piso} · {edif}'
        return 'ámbito territorial'

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        usuario = ctx['usuario']
        destino = self._describir_ambito(instance)
        tipo    = ctx['tipo']
        verb    = 'reasignado' if ctx.get('restored') else 'asignado'
        self._audit_registrar(
            instance, self.ASIGNACION_USUARIO, actor,
            f'{usuario.username} {verb} a {destino} como {tipo}.',
            datos_extra={
                'usuario_id': usuario.id,
                'ambito': instance.ambito,
                'local_id': instance.local_id,
                'edificio_id': instance.edificio_id,
                'piso': instance.piso,
                'espacio_id': instance.espacio_id,
                'tipo_responsabilidad': tipo,
            },
        )

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        if cambios:
            destino = self._describir_ambito(instance)
            self._audit_registrar(
                instance, self.ACTUALIZACION, actor,
                f'Asignación en {destino} actualizada.',
                datos_extra={
                    'cambios': cambios,
                    'ambito': instance.ambito,
                    'local_id': instance.local_id,
                    'edificio_id': instance.edificio_id,
                    'piso': instance.piso,
                    'espacio_id': instance.espacio_id,
                },
            )

    def _audit_on_delete(self, instance, actor):
        destino = self._describir_ambito(instance)
        self._audit_registrar(
            instance, self.RETIRO_USUARIO, actor,
            f'{instance.usuario.username} retirado de {destino}.',
            datos_extra={
                'usuario_id': instance.usuario_id,
                'ambito': instance.ambito,
                'local_id': instance.local_id,
                'edificio_id': instance.edificio_id,
                'piso': instance.piso,
                'espacio_id': instance.espacio_id,
            },
        )

    # ── Métodos auxiliares ─────────────────────────────────────────────────────

    def get_opciones(self, actor: Usuario = None) -> dict:
        return self.repository.get_opciones(actor=actor)

    def _resolver_relaciones(self, data: dict) -> dict:
        """
        Resuelve y valida las entidades involucradas según el ámbito territorial:
        - Si ámbito es sede: exige local_id.
        - Si ámbito es edificio: exige edificio_id; autoderiva local = edificio.local.
        - Si ámbito es piso: exige edificio_id y piso; autoderiva local = edificio.local.
        - Si ámbito es espacio: exige espacio_id; autoderiva edificio, piso y local.
        """
        errors = {}
        usuario_id = data.get('usuario_id')
        usuario = self.repository.get_usuario_by_id(usuario_id) if usuario_id else None
        if usuario is None:
            errors['usuario_id'] = 'El usuario no existe o está inactivo.'

        ambito = data.get('ambito') or EspacioUsuario.AMBITO_ESPACIO
        local = None
        edificio = None
        espacio = None
        piso = data.get('piso') or ''
        if isinstance(piso, str):
            piso = piso.strip()
        else:
            piso = str(piso) if piso is not None else ''

        if ambito == EspacioUsuario.AMBITO_SEDE:
            local_id = data.get('local_id')
            if not local_id:
                errors['local_id'] = 'Este campo es obligatorio para el ámbito de sede.'
            else:
                local = self.repository.get_local_by_id(local_id)
                if local is None:
                    errors['local_id'] = 'El local no existe o está eliminado.'
            if data.get('edificio_id'):
                errors['edificio_id'] = 'Una asignación de nivel sede no debe especificar edificio.'
            if data.get('piso'):
                errors['piso'] = 'Una asignación de nivel sede no debe especificar piso.'
            if data.get('espacio_id'):
                errors['espacio_id'] = 'Una asignación de nivel sede no debe especificar espacio individual.'

        elif ambito == EspacioUsuario.AMBITO_EDIFICIO:
            edificio_id = data.get('edificio_id')
            if not edificio_id:
                errors['edificio_id'] = 'Este campo es obligatorio para el ámbito de edificio.'
            else:
                edificio = self.repository.get_edificio_by_id(edificio_id)
                if edificio is None:
                    errors['edificio_id'] = 'El edificio no existe o está eliminado.'
                else:
                    local = edificio.local
                    local_id = data.get('local_id')
                    if local_id and int(local_id) != local.id:
                        errors['local_id'] = 'El local especificado no coincide con el local del edificio.'
            if data.get('piso'):
                errors['piso'] = 'Una asignación de nivel edificio no debe especificar piso.'
            if data.get('espacio_id'):
                errors['espacio_id'] = 'Una asignación de nivel edificio no debe especificar espacio individual.'

        elif ambito == EspacioUsuario.AMBITO_PISO:
            edificio_id = data.get('edificio_id')
            if not edificio_id:
                errors['edificio_id'] = 'Este campo es obligatorio para el ámbito de piso.'
            else:
                edificio = self.repository.get_edificio_by_id(edificio_id)
                if edificio is None:
                    errors['edificio_id'] = 'El edificio no existe o está eliminado.'
                else:
                    local = edificio.local
                    local_id = data.get('local_id')
                    if local_id and int(local_id) != local.id:
                        errors['local_id'] = 'El local especificado no coincide con el local del edificio.'

            if not piso:
                errors['piso'] = 'Este campo es obligatorio para el ámbito de piso.'
            if data.get('espacio_id'):
                errors['espacio_id'] = 'Una asignación de nivel piso no debe especificar espacio individual.'

        elif ambito == EspacioUsuario.AMBITO_ESPACIO:
            espacio_id = data.get('espacio_id')
            if not espacio_id:
                errors['espacio_id'] = 'El espacio no existe o está eliminado.'
            else:
                espacio = self.repository.get_espacio_by_id(espacio_id)
                if espacio is None:
                    errors['espacio_id'] = 'El espacio no existe o está eliminado.'
                else:
                    edificio = espacio.edificio
                    if edificio:
                        local = edificio.local
                        local_id = data.get('local_id')
                        if local_id and int(local_id) != local.id:
                            errors['local_id'] = 'El local especificado no coincide con el del espacio.'
                        edificio_id = data.get('edificio_id')
                        if edificio_id and int(edificio_id) != edificio.id:
                            errors['edificio_id'] = 'El edificio especificado no coincide con el del espacio.'
                    piso_input = data.get('piso')
                    if piso_input and espacio.piso and str(piso_input).strip() != str(espacio.piso).strip():
                        errors['piso'] = 'El piso especificado no coincide con el del espacio.'
                    piso = espacio.piso or ''
        else:
            errors['ambito'] = f"Ámbito '{ambito}' no válido."

        if errors:
            raise ValidationError(errors)

        return {
            'usuario': usuario,
            'ambito': ambito,
            'local': local,
            'edificio': edificio,
            'piso': piso if ambito in (EspacioUsuario.AMBITO_PISO, EspacioUsuario.AMBITO_ESPACIO) else '',
            'espacio': espacio,
        }

    def _validar_unicidad(
        self,
        ambito_o_espacio_id: str | int = EspacioUsuario.AMBITO_ESPACIO,
        usuario_id: int | None = None,
        local_id: int | None = None,
        edificio_id: int | None = None,
        piso: str | None = None,
        espacio_id: int | None = None,
        exclude_id: int | None = None,
        ambito: str | None = None,
    ) -> None:
        """
        Valida que no exista otra asignación activa vigente para el mismo usuario y entidad territorial.
        Soporta firma polimórfica:
        - Nueva: _validar_unicidad(ambito='piso', usuario_id=1, edificio_id=2, piso='2')
        - Legacy posicional: _validar_unicidad(espacio_id, usuario_id, exclude_id)
        """
        if isinstance(ambito_o_espacio_id, int):
            espacio_id = ambito_o_espacio_id
            effective_ambito = EspacioUsuario.AMBITO_ESPACIO
        else:
            effective_ambito = ambito or ambito_o_espacio_id

        existing = self.repository.get_by_scope(
            ambito=effective_ambito,
            usuario_id=usuario_id,
            local_id=local_id,
            edificio_id=edificio_id,
            piso=piso,
            espacio_id=espacio_id,
            exclude_id=exclude_id,
            only_active=True,
        )
        if existing:
            raise ValidationError({'detail': 'El usuario ya está asignado a este ámbito.'})
