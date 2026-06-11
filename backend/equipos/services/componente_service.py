from equipos.repositories.componente_repository import ComponenteRepository
from equipos.repositories.equipo_repository import EquipoRepository
from equipos.models import Componente
from equipos.exceptions import ComponenteNoEncontrado, EquipoNoEncontrado


class ComponenteService:
    def __init__(self, componente_repository: ComponenteRepository, equipo_repository: EquipoRepository):
        self.repo        = componente_repository
        self.equipo_repo = equipo_repository

    def listar_componentes(self, equipo_id: int) -> list:
        if self.equipo_repo.get_by_id(equipo_id) is None:
            raise EquipoNoEncontrado(f"Equipo {equipo_id} no encontrado")
        return self.repo.get_by_equipo(equipo_id)

    def crear_componente(self, datos: dict) -> Componente:
        return self.repo.create(**datos)

    def actualizar_componente(self, componente_id: int, datos: dict) -> Componente:
        componente = self.repo.get_by_id(componente_id)
        if componente is None:
            raise ComponenteNoEncontrado(f"Componente {componente_id} no encontrado")
        return self.repo.update(componente, **datos)

    def eliminar_componente(self, componente_id: int) -> None:
        componente = self.repo.get_by_id(componente_id)
        if componente is None:
            raise ComponenteNoEncontrado(f"Componente {componente_id} no encontrado")
        self.repo.delete(componente)
