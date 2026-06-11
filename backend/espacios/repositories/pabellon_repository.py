from typing import Optional
from espacios.models import Pabellon
from usuarios.repositories.base_repository import BaseRepository


class PabellonRepository(BaseRepository[Pabellon]):
    def __init__(self):
        super().__init__(Pabellon)

    def get_all(self):
        return Pabellon.objects.all().order_by('id_pabellon')

    def get_by_id(self, pabellon_id: int) -> Optional[Pabellon]:
        return Pabellon.objects.filter(id_pabellon=pabellon_id).first()

    @staticmethod
    def get_by_nombre(nombre: str) -> Optional[Pabellon]:
        return Pabellon.objects.filter(nombre=nombre).first()

    @staticmethod
    def create(**datos) -> Pabellon:
        return Pabellon.objects.create(**datos)

    @staticmethod
    def update(pabellon: Pabellon, **datos) -> Pabellon:
        for field, value in datos.items():
            setattr(pabellon, field, value)
        pabellon.save()
        return pabellon
