from typing import Optional
from equipos.models import Componente
from usuarios.repositories.base_repository import BaseRepository


class ComponenteRepository(BaseRepository[Componente]):
    def __init__(self):
        super().__init__(Componente)

    def get_by_equipo(self, equipo_id: int):
        return Componente.objects.filter(equipo__id_equipo=equipo_id).order_by('id_componente')

    def get_by_id(self, componente_id: int) -> Optional[Componente]:
        return Componente.objects.filter(id_componente=componente_id).first()

    @staticmethod
    def create(**datos) -> Componente:
        return Componente.objects.create(**datos)

    @staticmethod
    def update(componente: Componente, **datos) -> Componente:
        for field, value in datos.items():
            setattr(componente, field, value)
        componente.save()
        return componente
