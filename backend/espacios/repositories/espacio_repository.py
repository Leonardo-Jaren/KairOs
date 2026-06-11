from typing import Optional
from espacios.models import Espacio
from usuarios.repositories.base_repository import BaseRepository


class EspacioRepository(BaseRepository[Espacio]):
    def __init__(self):
        super().__init__(Espacio)

    def get_all(self):
        return Espacio.objects.select_related('pabellon').all().order_by('id_espacio')

    def get_by_id(self, espacio_id: int) -> Optional[Espacio]:
        return Espacio.objects.select_related('pabellon').filter(id_espacio=espacio_id).first()

    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Espacio]:
        return Espacio.objects.filter(codigo_espacio=codigo).first()

    @staticmethod
    def get_by_pabellon(pabellon_id: int):
        return Espacio.objects.select_related('pabellon').filter(
            pabellon__id_pabellon=pabellon_id
        ).order_by('id_espacio')

    @staticmethod
    def create(**datos) -> Espacio:
        return Espacio.objects.create(**datos)

    @staticmethod
    def update(espacio: Espacio, **datos) -> Espacio:
        for field, value in datos.items():
            setattr(espacio, field, value)
        espacio.save()
        return espacio
