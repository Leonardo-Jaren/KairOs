from rest_framework.exceptions import ValidationError

from equipos.models import Equipo
from equipos.repositories import EquipoRepository
from shared.base import BaseService
from usuarios.models import Usuario


class EquipoService(BaseService):
    """Aplica las reglas de negocio para gestionar equipos informaticos."""

    def __init__(self):
        self.repository = EquipoRepository()

    def listar(
        self,
        busqueda: str = '',
        tipo_equipo: str = '',
        estado: str = '',
        espacio_id: int | None = None,
    ):
        """Lista equipos aplicando filtros normalizados."""
        return self.repository.listar(
            busqueda=busqueda.strip(),
            tipo_equipo=tipo_equipo.strip(),
            estado=estado.strip(),
            espacio_id=espacio_id,
        )

    def create(self, data: dict, actor: Usuario) -> Equipo:
        """Crea un equipo validando unicidad de codigo y numero de serie."""
        clean_data = self._normalizar(data)
        self._validar_unicidad(clean_data)
        instance = self.repository.create(
            **clean_data,
            created_by=actor,
            updated_by=actor,
        )
        return self.repository.get_by_id(instance.id)

    def update(self, id: int, data: dict, actor: Usuario) -> Equipo:
        """Actualiza un equipo conservando la unicidad de sus identificadores."""
        instance = self.get_by_id(id)
        clean_data = self._normalizar(data, partial=True)
        self._validar_unicidad(clean_data, exclude_id=instance.id)
        clean_data['updated_by'] = actor
        self.repository.update(instance, **clean_data)
        return self.repository.get_by_id(instance.id)

    def delete(self, id: int, actor: Usuario) -> None:
        """Realiza borrado logico del equipo."""
        instance = self.get_by_id(id)
        self.repository.soft_delete(instance, actor)

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
