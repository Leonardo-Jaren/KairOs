from equipos.repositories.equipo_repository import EquipoRepository
from equipos.models import Equipo
from equipos.exceptions import EquipoNoEncontrado, DatosInvalidos


class EquipoService:
    def __init__(self, equipo_repository: EquipoRepository):
        self.repo = equipo_repository

    def listar_equipos(self, estado: str = None, espacio_id: int = None) -> list:
        return self.repo.get_all(estado=estado, espacio_id=espacio_id)

    def get_equipo(self, equipo_id: int) -> Equipo:
        equipo = self.repo.get_by_id(equipo_id)
        if equipo is None:
            raise EquipoNoEncontrado(f"Equipo {equipo_id} no encontrado")
        return equipo

    def crear_equipo(self, datos: dict) -> Equipo:
        if self.repo.get_by_codigo(datos.get("codigo", "")):
            raise DatosInvalidos("El código de equipo ya está registrado")
        return self.repo.create(**datos)

    def actualizar_equipo(self, equipo_id: int, datos: dict) -> Equipo:
        equipo = self.get_equipo(equipo_id)
        codigo_nuevo = datos.get("codigo")
        if codigo_nuevo and codigo_nuevo != equipo.codigo:
            if self.repo.get_by_codigo(codigo_nuevo):
                raise DatosInvalidos("El código de equipo ya está registrado")
        return self.repo.update(equipo, **datos)

    def cambiar_estado(self, equipo_id: int, estado: str) -> Equipo:
        estados_validos = [e.value for e in Equipo.Estado]
        if estado not in estados_validos:
            raise DatosInvalidos(f"Estado inválido. Opciones: {estados_validos}")
        equipo = self.get_equipo(equipo_id)
        return self.repo.update(equipo, estado=estado)

    def eliminar_equipo(self, equipo_id: int) -> None:
        equipo = self.get_equipo(equipo_id)
        self.repo.delete(equipo)
