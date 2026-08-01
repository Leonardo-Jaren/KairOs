from rest_framework.exceptions import ValidationError

from espacios.models import Espacio
from espacios.repositories.espacio_repository import EspacioRepository
from shared.base_service import BaseService
from usuarios.models import Usuario


class EspacioService(BaseService):
    """Aplica las reglas de negocio para gestionar espacios."""

    def __init__(self):
        self.repository = EspacioRepository()

    def listar(
        self,
        busqueda: str = '',
        tipo: str = '',
        activo: bool | None = None,
        pabellon: str = '',
    ):
        """Lista espacios aplicando filtros normalizados."""
        return self.repository.listar(
            busqueda=busqueda.strip(),
            tipo=tipo.strip(),
            activo=activo,
            pabellon=pabellon.strip(),
        )

    def create(self, data: dict, actor: Usuario) -> Espacio:
        """Crea o restaura un espacio con código único."""
        clean_data = self._normalizar(data)
        existing = self.repository.get_by_codigo(clean_data['codigo_espacio'])
        if existing and existing.is_deleted:
            return self.repository.restore(existing, clean_data, actor)
        self._validar_codigo(clean_data['codigo_espacio'])
        instance = self.repository.create(
            **clean_data,
            created_by=actor,
            updated_by=actor,
        )
        return self.repository.get_by_id(instance.id)

    def update(self, id: int, data: dict, actor: Usuario) -> Espacio:
        """Actualiza un espacio conservando auditoría y unicidad."""
        instance = self.get_by_id(id)
        clean_data = self._normalizar(data, partial=True)
        codigo = clean_data.get('codigo_espacio', instance.codigo_espacio)
        self._validar_codigo(codigo, exclude_id=instance.id)
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def delete(self, id: int, actor: Usuario) -> None:
        """Realiza borrado lógico del espacio."""
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)

    def get_estadisticas(self) -> dict:
        """Retorna indicadores para la cabecera del módulo."""
        return self.repository.get_estadisticas()

    def _normalizar(self, data: dict, partial: bool = False) -> dict:
        clean_data = data.copy()
        if 'codigo_espacio' in clean_data:
            clean_data['codigo_espacio'] = clean_data['codigo_espacio'].strip().upper()
        elif not partial:
            clean_data['codigo_espacio'] = ''
        for field in ['pabellon', 'piso']:
            if field in clean_data:
                clean_data[field] = clean_data[field].strip()
        return clean_data

    def _validar_codigo(
        self,
        codigo: str,
        exclude_id: int | None = None,
    ) -> None:
        if self.repository.get_by_codigo(codigo, exclude_id):
            raise ValidationError({
                'codigo_espacio': 'Ya existe un espacio con este código.'
            })
