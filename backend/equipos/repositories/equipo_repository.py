from typing import Optional
from equipos.models import Equipo
from usuarios.repositories.base_repository import BaseRepository


class EquipoRepository(BaseRepository[Equipo]):
    def __init__(self):
        super().__init__(Equipo)

    def get_all(self, estado: str = None, espacio_id: int = None):
        qs = Equipo.objects.select_related('espacio', 'responsable').order_by('id_equipo')
        if estado:
            qs = qs.filter(estado=estado)
        if espacio_id:
            qs = qs.filter(espacio__id_espacio=espacio_id)
        return qs

    def get_by_id(self, equipo_id: int) -> Optional[Equipo]:
        return (
            Equipo.objects
            .select_related('espacio', 'responsable')
            .prefetch_related('componentes')
            .filter(id_equipo=equipo_id)
            .first()
        )

    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Equipo]:
        return Equipo.objects.filter(codigo=codigo).first()

    @staticmethod
    def create(**datos) -> Equipo:
        return Equipo.objects.create(**datos)

    @staticmethod
    def update(equipo: Equipo, **datos) -> Equipo:
        for field, value in datos.items():
            setattr(equipo, field, value)
        equipo.save()
        return equipo
