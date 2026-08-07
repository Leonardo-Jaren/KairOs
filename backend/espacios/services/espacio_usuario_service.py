from rest_framework.exceptions import ValidationError

from espacios.models import EspacioUsuario
from espacios.repositories import EspacioUsuarioRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario


class EspacioUsuarioService(AuditableMixin, BaseService):
    """Aplica reglas para asignar usuarios a espacios físicos."""

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
    ):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            activo=activo,
            usuario_id=usuario_id,
            espacio_id=espacio_id,
        )

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Usuario = None):
        clean_data = data.copy()
        usuario, espacio = self._resolver_relaciones(clean_data)
        tipo = clean_data.get('tipo_responsabilidad', 'responsable')
        ctx = {'usuario': usuario, 'espacio': espacio, 'tipo': tipo}
        existing = self.repository.get_by_pair(espacio.id, usuario.id)
        if existing and existing.is_deleted:
            instance = self.repository.restore(existing, tipo, actor)
            return instance, {**ctx, 'restored': True}
        self._validar_unicidad(espacio.id, usuario.id)
        instance = self.repository.create(
            usuario=usuario,
            espacio=espacio,
            tipo_responsabilidad=tipo,
            activo=clean_data.get('activo', True),
            created_by=actor,
            updated_by=actor,
        )
        return instance, {**ctx, 'restored': False}

    def _do_update(self, id: int, data: dict, actor: Usuario = None) -> EspacioUsuario:
        instance = self.get_by_id(id)
        clean_data = data.copy()
        usuario_id = clean_data.pop('usuario_id', instance.usuario_id)
        espacio_id = clean_data.pop('espacio_id', instance.espacio_id)
        usuario, espacio = self._resolver_relaciones({
            'usuario_id': usuario_id,
            'espacio_id': espacio_id,
        })
        self._validar_unicidad(espacio.id, usuario.id, exclude_id=instance.id)
        clean_data.update({'usuario': usuario, 'espacio': espacio, 'updated_by': actor})
        return self.repository.update(instance, **clean_data)

    def _do_delete(self, id: int, actor: Usuario = None) -> EspacioUsuario:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        usuario = ctx['usuario']
        espacio = ctx['espacio']
        tipo    = ctx['tipo']
        verb    = 'reasignado' if ctx.get('restored') else 'asignado'
        self._audit_registrar(
            instance, self.ASIGNACION_USUARIO, actor,
            f'{usuario.username} {verb} a {espacio.codigo_espacio} como {tipo}.',
            datos_extra={
                'usuario_id': usuario.id,
                'espacio_id': espacio.id,
                'tipo_responsabilidad': tipo,
            },
        )

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        if cambios:
            self._audit_registrar(
                instance, self.ACTUALIZACION, actor,
                f'Asignación en {instance.espacio.codigo_espacio} actualizada.',
                datos_extra={'cambios': cambios},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(
            instance, self.RETIRO_USUARIO, actor,
            f'{instance.usuario.username} retirado de {instance.espacio.codigo_espacio}.',
            datos_extra={
                'usuario_id': instance.usuario_id,
                'espacio_id': instance.espacio_id,
            },
        )

    # ── Métodos auxiliares ─────────────────────────────────────────────────────

    def get_opciones(self) -> dict:
        return self.repository.get_opciones()

    def _resolver_relaciones(self, data: dict):
        usuario = self.repository.get_usuario_by_id(data.get('usuario_id'))
        espacio = self.repository.get_espacio_by_id(data.get('espacio_id'))
        errors = {}
        if usuario is None:
            errors['usuario_id'] = 'El usuario no existe o está inactivo.'
        if espacio is None:
            errors['espacio_id'] = 'El espacio no existe o está eliminado.'
        if errors:
            raise ValidationError(errors)
        return usuario, espacio

    def _validar_unicidad(
        self,
        espacio_id: int,
        usuario_id: int,
        exclude_id: int | None = None,
    ) -> None:
        existing = self.repository.get_by_pair(espacio_id, usuario_id, exclude_id)
        if existing:
            raise ValidationError({'detail': 'El usuario ya está asignado a este espacio.'})
