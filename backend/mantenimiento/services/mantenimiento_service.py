from rest_framework.exceptions import ValidationError

from mantenimiento.models import Mantenimiento
from mantenimiento.repositories import MantenimientoRepository
from shared.base_service import BaseService
from usuarios.models import Usuario


class MantenimientoService(BaseService):
    """Aplica las reglas de negocio para gestionar tickets de mantenimiento."""

    def __init__(self):
        self.repository = MantenimientoRepository()

    def listar(
        self,
        busqueda: str = '',
        estado: str = '',
        tipo_mantenimiento: str = '',
        equipo_id: int | None = None,
    ):
        """Lista tickets aplicando filtros normalizados."""
        return self.repository.listar(
            busqueda=busqueda.strip(),
            estado=estado.strip(),
            tipo_mantenimiento=tipo_mantenimiento.strip(),
            equipo_id=equipo_id,
        )

    def create(self, data: dict, actor: Usuario) -> Mantenimiento:
        """Crea un ticket de mantenimiento junto a sus tecnicos asignados."""
        clean_data = data.copy()
        tecnico_ids = clean_data.pop('tecnicos_ids', [])
        equipo = self._resolver_equipo(clean_data.pop('equipo_id'))
        self._validar_tecnicos(tecnico_ids)

        instance = self.repository.create(
            **clean_data,
            equipo=equipo,
            created_by=actor,
            updated_by=actor,
        )
        self.repository.sync_tecnicos(instance, tecnico_ids)
        return self.repository.get_by_id(instance.id)

    def update(self, id: int, data: dict, actor: Usuario) -> Mantenimiento:
        """Actualiza un ticket y resincroniza sus tecnicos asignados."""
        instance = self.get_by_id(id)
        clean_data = data.copy()
        tecnico_ids = clean_data.pop('tecnicos_ids', None)

        if 'equipo_id' in clean_data:
            clean_data['equipo'] = self._resolver_equipo(clean_data.pop('equipo_id'))

        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)

        if tecnico_ids is not None:
            self._validar_tecnicos(tecnico_ids)
            self.repository.sync_tecnicos(instance, tecnico_ids)

        return self.repository.get_by_id(instance.id)

    def delete(self, id: int, actor: Usuario) -> None:
        """Realiza borrado logico del ticket de mantenimiento."""
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)

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
