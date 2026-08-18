import re

from rest_framework.exceptions import ValidationError

from espacios.models import Espacio
from espacios.repositories.espacio_repository import EspacioRepository
from shared.base import BaseService
from shared.mixins import AuditableMixin
from usuarios.models import Usuario


class EspacioService(AuditableMixin, BaseService):
    """Aplica las reglas de negocio para gestionar espacios."""

    ALTA          = 'espacio.alta'
    ACTUALIZACION = 'espacio.actualizacion'
    DESACTIVACION = 'espacio.desactivacion'
    DISPOSICION    = 'espacio.disposicion'

    def __init__(self):
        self.repository = EspacioRepository()

    def listar(
        self,
        busqueda: str = '',
        tipo: str = '',
        activo: bool | None = None,
        pabellon: str = '',
        edificio: str = '',
        edificio_id: int | None = None,
    ):
        return self.repository.listar(
            busqueda=busqueda.strip(),
            tipo=tipo.strip(),
            activo=activo,
            pabellon=pabellon.strip(),
            edificio=edificio.strip(),
            edificio_id=edificio_id,
        )

    # ── Hooks de lógica de negocio ─────────────────────────────────────────────

    def _do_create(self, data: dict, actor: Usuario = None):
        clean_data = self._normalizar(data)
        self._sincronizar_pabellon(clean_data)
        existing = self.repository.get_by_codigo(clean_data['codigo_espacio'])
        if existing and existing.is_deleted:
            instance = self.repository.restore(existing, clean_data, actor)
            return instance, {'restored': True}
        self._validar_codigo(clean_data['codigo_espacio'])
        instance = self.repository.create(**clean_data, created_by=actor, updated_by=actor)
        instance = self.repository.get_by_id(instance.id)
        return instance, {'restored': False}

    def _do_update(self, id: int, data: dict, actor: Usuario = None) -> Espacio:
        instance = self.get_by_id(id)
        clean_data = self._normalizar(data, partial=True)
        self._sincronizar_pabellon(clean_data, edificio_actual=instance.edificio)
        codigo = clean_data.get('codigo_espacio', instance.codigo_espacio)
        self._validar_codigo(codigo, exclude_id=instance.id)
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def _do_delete(self, id: int, actor: Usuario = None) -> Espacio:
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)
        return instance

    # ── Hooks de auditoría ─────────────────────────────────────────────────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        desc = (
            f'Espacio {instance.codigo_espacio} reactivado.'
            if ctx.get('restored')
            else f'Espacio {instance.codigo_espacio} registrado.'
        )
        self._audit_registrar(instance, self.ALTA, actor, desc)

    def _audit_on_update(self, cambios: list, instance, actor, ctx: dict | None = None):
        if cambios:
            self._audit_registrar(
                instance, self.ACTUALIZACION, actor,
                f'Espacio {instance.codigo_espacio} actualizado.',
                datos_extra={'cambios': cambios},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(
            instance, self.DESACTIVACION, actor,
            f'Espacio {instance.codigo_espacio} desactivado.',
        )

    # ── Métodos auxiliares ─────────────────────────────────────────────────────

    def get_estadisticas(self) -> dict:
        return self.repository.get_estadisticas()

    def actualizar_disposicion(
        self,
        id: int,
        data: dict,
        actor: Usuario = None,
    ) -> Espacio:
        """Guarda un plano validando que sus equipos pertenezcan al espacio."""
        instance = self.get_by_id(id)
        equipos_validos = {
            equipo.id for equipo in getattr(instance, 'equipos_vigentes', [])
        }
        equipos_solicitados = {puesto['equipo_id'] for puesto in data['puestos']}
        equipos_ajenos = equipos_solicitados - equipos_validos
        if equipos_ajenos:
            raise ValidationError({
                'puestos': 'El plano contiene equipos que no pertenecen a este espacio.'
            })

        configuracion = {
            'columnas': data['columnas'],
            'filas': data['filas'],
            'puestos': [
                {
                    'equipo_id': puesto['equipo_id'],
                    'fila': puesto['fila'],
                    'columna': puesto['columna'],
                    'es_docente': puesto.get('es_docente', False),
                }
                for puesto in data['puestos']
            ],
        }
        self.repository.update(
            instance,
            configuracion_plano=configuracion,
            updated_by=actor,
        )
        updated = self.repository.get_by_id(instance.id)
        self._audit_registrar(
            updated,
            self.DISPOSICION,
            actor,
            f'Plano de {updated.codigo_espacio} actualizado.',
            datos_extra={
                'columnas': configuracion['columnas'],
                'filas': configuracion['filas'],
                'equipos_ubicados': len(configuracion['puestos']),
            },
        )
        return updated

    def _normalizar(self, data: dict, partial: bool = False) -> dict:
        clean_data = data.copy()
        if 'codigo_espacio' in clean_data:
            clean_data['codigo_espacio'] = clean_data['codigo_espacio'].strip().upper()
        elif not partial:
            clean_data['codigo_espacio'] = ''
        for field in ['pabellon', 'piso']:
            if field in clean_data:
                clean_data[field] = clean_data[field].strip()
        if 'piso' in clean_data:
            clean_data['piso'] = re.sub(r'^piso\s*', '', clean_data['piso'], flags=re.IGNORECASE).strip()
            if not clean_data['piso']:
                raise ValidationError({
                    'piso': 'Ingrese el número o nombre corto del piso.'
                })
        return clean_data

    @staticmethod
    def _sincronizar_pabellon(clean_data: dict, edificio_actual=None) -> None:
        """Completa el campo histórico cuando el espacio pertenece a un edificio."""
        edificio = clean_data.get('edificio', edificio_actual)
        if edificio is not None and not clean_data.get('pabellon'):
            clean_data['pabellon'] = edificio.nombre

    def _validar_codigo(self, codigo: str, exclude_id: int | None = None) -> None:
        if self.repository.get_by_codigo(codigo, exclude_id):
            raise ValidationError({'codigo_espacio': 'Ya existe un espacio con este código.'})
