from rest_framework.exceptions import ValidationError

from espacios.repositories.local_repository import LocalRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario


class LocalService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para administrar locales físicos."""

    ALTA = 'local.alta'
    ACTUALIZACION = 'local.actualizacion'
    DESACTIVACION = 'local.desactivacion'

    def __init__(self):
        self.repository = LocalRepository()

    def listar(
        self,
        busqueda: str = '',
        activo: bool | None = None,
        actor: Usuario | None = None,
        solo_asignables: bool = False,
    ):
        """Lista locales vigentes aplicando filtros normalizados."""
        sede_ids = None
        if solo_asignables and actor and actor.rol != 'superadmin' and not actor.is_superuser:
            sede_ids = list(
                actor.usuario_sedes.filter(activo=True).values_list('local_id', flat=True)
            )
        return self.repository.listar(
            busqueda=busqueda.strip(),
            activo=activo,
            sede_ids=sede_ids,
        )

    def _do_create(self, data: dict, actor: Usuario = None):
        clean_data = self._normalizar(data)
        existing = self.repository.get_by_codigo(clean_data['codigo'])
        if existing and existing.is_deleted:
            return self.repository.restore(existing, clean_data, actor), {'restored': True}
        self._validar_codigo(clean_data['codigo'])
        instance = self.repository.create(
            **clean_data,
            created_by=actor,
            updated_by=actor,
        )
        return self.repository.get_by_id(instance.id), {'restored': False}

    def _do_update(self, id: int, data: dict, actor: Usuario = None):
        instance = self.get_by_id(id)
        clean_data = self._normalizar(data, partial=True)
        codigo = clean_data.get('codigo', instance.codigo)
        self._validar_codigo(codigo, exclude_id=instance.id)
        self._validar_desactivacion(instance, clean_data)
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def _do_delete(self, id: int, actor: Usuario = None):
        instance = self.get_by_id(id)
        self._validar_desactivacion(instance, {'activo': False})
        self.repository.soft_delete(instance, actor)
        return instance

    def _validar_desactivacion(self, instance, data: dict) -> None:
        """Bloquea retirar un local con edificios aún vigentes."""
        if data.get('activo') is False and self.repository.tiene_edificios_vigentes(instance):
            raise ValidationError({
                'activo': (
                    'No se puede desactivar este local porque tiene edificios '
                    'vigentes relacionados.'
                )
            })

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        descripcion = (
            f'Local {instance.codigo} reactivado.'
            if ctx.get('restored')
            else f'Local {instance.codigo} registrado.'
        )
        self._audit_registrar(instance, self.ALTA, actor, descripcion)

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        if cambios:
            self._audit_registrar(
                instance,
                self.ACTUALIZACION,
                actor,
                f'Local {instance.codigo} actualizado.',
                datos_extra={'cambios': cambios},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(
            instance,
            self.DESACTIVACION,
            actor,
            f'Local {instance.codigo} desactivado.',
        )

    def _normalizar(self, data: dict, partial: bool = False) -> dict:
        clean_data = data.copy()
        if 'codigo' in clean_data:
            clean_data['codigo'] = clean_data['codigo'].strip().upper()
        elif not partial:
            clean_data['codigo'] = ''
        if not partial and 'tipo' not in clean_data:
            clean_data['tipo'] = 'sede'
        for field in ['nombre', 'ciudad', 'tipo', 'descripcion']:
            if field in clean_data:
                clean_data[field] = clean_data[field].strip()
        for field in ['codigo', 'nombre', 'ciudad', 'tipo']:
            if field in clean_data and not clean_data[field]:
                raise ValidationError({field: 'Este campo es obligatorio.'})
        if not partial:
            for field in ['codigo', 'nombre', 'ciudad', 'tipo']:
                if field not in clean_data:
                    raise ValidationError({field: 'Este campo es obligatorio.'})
        return clean_data

    def _validar_codigo(self, codigo: str, exclude_id: int | None = None) -> None:
        if self.repository.get_by_codigo(codigo, exclude_id):
            raise ValidationError({'codigo': 'Ya existe un local con este código.'})
