from rest_framework.exceptions import ValidationError

from equipos.models import Equipo
from equipos.repositories import EquipoRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario


class EquipoService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para gestionar equipos informaticos."""

    ALTA                 = 'equipo.alta'
    BAJA                 = 'equipo.baja'
    ACTUALIZACION        = 'equipo.actualizacion'
    CAMBIO_ESTADO        = 'equipo.cambio_estado'
    ASIGNACION_ESPACIO   = 'equipo.asignacion_espacio'
    REASIGNACION_ESPACIO = 'equipo.reasignacion_espacio'
    CAMBIO_RESPONSABLE   = 'equipo.cambio_responsable'

    def __init__(self):
        self.repository = EquipoRepository()

    def listar(
        self,
        busqueda: str = '',
        tipo_equipo: str = '',
        estado: str = '',
        espacio_id: int | None = None,
    ):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            tipo_equipo=tipo_equipo.strip(),
            estado=estado.strip(),
            espacio_id=espacio_id,
        )

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Usuario = None) -> Equipo:
        clean_data = self._normalizar(data)
        self._validar_unicidad(clean_data)
        instance = self.repository.create(**clean_data, created_by=actor, updated_by=actor)
        return self.repository.get_by_id(instance.id)

    def _do_update(self, id: int, data: dict, actor: Usuario = None) -> Equipo:
        instance = self.get_by_id(id)
        clean_data = self._normalizar(data, partial=True)
        self._validar_unicidad(clean_data, exclude_id=instance.id)
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def _do_delete(self, id: int, actor: Usuario = None) -> Equipo:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        self._audit_registrar(instance, self.ALTA, actor, f'Equipo {instance.codigo} registrado.')

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        restantes = []
        for cambio in cambios:
            campo, antes, despues = cambio['campo'], cambio['antes'], cambio['despues']
            if campo == 'Estado':
                self._audit_registrar(
                    instance, self.CAMBIO_ESTADO, actor,
                    f'{instance.codigo}: estado cambió a "{despues}".',
                    datos_extra={'cambios': [cambio]},
                )
            elif campo == 'Espacio asignado':
                tipo = self.ASIGNACION_ESPACIO if antes == '—' else self.REASIGNACION_ESPACIO
                desc = (
                    f'{instance.codigo} asignado a espacio (id={despues}).'
                    if antes == '—'
                    else f'{instance.codigo} movido de espacio (id={antes}) a (id={despues}).'
                )
                self._audit_registrar(instance, tipo, actor, desc, datos_extra={'cambios': [cambio]})
            elif campo == 'Usuario asignado/responsable':
                self._audit_registrar(
                    instance, self.CAMBIO_RESPONSABLE, actor,
                    f'Responsable de {instance.codigo} cambió a "{despues}".',
                    datos_extra={'cambios': [cambio]},
                )
            else:
                restantes.append(cambio)
        if restantes:
            self._audit_registrar(
                instance, self.ACTUALIZACION, actor,
                f'Equipo {instance.codigo} actualizado.',
                datos_extra={'cambios': restantes},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(instance, self.BAJA, actor, f'Equipo {instance.codigo} dado de baja.')

    def get_estadisticas(self) -> dict:
        """Retorna indicadores para la cabecera del modulo."""
        return self.repository.get_estadisticas()

    def get_opciones(self):
        """Retorna equipos vigentes para poblar selects de otros modulos."""
        return self.repository.get_opciones()

    def _normalizar(self, data: dict, partial: bool = False) -> dict:
        clean_data = data.copy()
        if 'codigo' in clean_data:
            clean_data['codigo'] = clean_data['codigo'].strip().upper()
        if 'numero_serie' in clean_data:
            clean_data['numero_serie'] = clean_data['numero_serie'].strip().upper()
        return clean_data

    def _validar_unicidad(self, data: dict, exclude_id: int | None = None) -> None:
        """Valida campos unicos sin acceder al ORM fuera del repository."""
        errors = {}
        codigo = data.get('codigo')
        numero_serie = data.get('numero_serie')

        if codigo and self.repository.get_by_codigo(codigo, exclude_id):
            errors['codigo'] = 'Ya existe un equipo con este codigo.'
        if numero_serie and self.repository.get_by_numero_serie(numero_serie, exclude_id):
            errors['numero_serie'] = 'Ya existe un equipo con este numero de serie.'

        if errors:
            raise ValidationError(errors)
