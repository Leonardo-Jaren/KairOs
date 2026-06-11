from espacios.repositories.pabellon_repository import PabellonRepository
from espacios.models import Pabellon
from espacios.exceptions import PabellonNoEncontrado, DatosInvalidos


class PabellonService:
    def __init__(self, pabellon_repository: PabellonRepository):
        self.repo = pabellon_repository

    def listar_pabellones(self) -> list:
        return self.repo.get_all()

    def get_pabellon(self, pabellon_id: int) -> Pabellon:
        pabellon = self.repo.get_by_id(pabellon_id)
        if pabellon is None:
            raise PabellonNoEncontrado(f"Pabellón {pabellon_id} no encontrado")
        return pabellon

    def crear_pabellon(self, datos: dict) -> Pabellon:
        if self.repo.get_by_nombre(datos.get("nombre", "")):
            raise DatosInvalidos("Ya existe un pabellón con ese nombre")
        return self.repo.create(**datos)

    def actualizar_pabellon(self, pabellon_id: int, datos: dict) -> Pabellon:
        pabellon = self.get_pabellon(pabellon_id)
        nombre_nuevo = datos.get("nombre")
        if nombre_nuevo and nombre_nuevo != pabellon.nombre:
            if self.repo.get_by_nombre(nombre_nuevo):
                raise DatosInvalidos("Ya existe un pabellón con ese nombre")
        return self.repo.update(pabellon, **datos)

    def eliminar_pabellon(self, pabellon_id: int) -> None:
        pabellon = self.get_pabellon(pabellon_id)
        self.repo.delete(pabellon)
