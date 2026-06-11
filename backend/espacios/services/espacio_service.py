from espacios.repositories.espacio_repository import EspacioRepository
from espacios.models import Espacio
from espacios.exceptions import EspacioNoEncontrado, DatosInvalidos


class EspacioService:
    def __init__(self, espacio_repository: EspacioRepository):
        self.repo = espacio_repository

    def listar_espacios(self, pabellon_id: int = None) -> list:
        if pabellon_id is not None:
            return self.repo.get_by_pabellon(pabellon_id)
        return self.repo.get_all()

    def get_espacio(self, espacio_id: int) -> Espacio:
        espacio = self.repo.get_by_id(espacio_id)
        if espacio is None:
            raise EspacioNoEncontrado(f"Espacio {espacio_id} no encontrado")
        return espacio

    def crear_espacio(self, datos: dict) -> Espacio:
        if self.repo.get_by_codigo(datos.get("codigo_espacio", "")):
            raise DatosInvalidos("El código de espacio ya está registrado")
        return self.repo.create(**datos)

    def actualizar_espacio(self, espacio_id: int, datos: dict) -> Espacio:
        espacio = self.get_espacio(espacio_id)
        codigo_nuevo = datos.get("codigo_espacio")
        if codigo_nuevo and codigo_nuevo != espacio.codigo_espacio:
            if self.repo.get_by_codigo(codigo_nuevo):
                raise DatosInvalidos("El código de espacio ya está registrado")
        return self.repo.update(espacio, **datos)

    def eliminar_espacio(self, espacio_id: int) -> None:
        espacio = self.get_espacio(espacio_id)
        self.repo.delete(espacio)
