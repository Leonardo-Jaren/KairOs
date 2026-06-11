from typing import Optional
from incidencias.models import Incidencia
from usuarios.repositories.base_repository import BaseRepository


class IncidenciaRepository(BaseRepository[Incidencia]):

    def __init__(self):
        super().__init__(Incidencia)

    def _base_qs(self):
        return (
            Incidencia.objects
            .select_related(
                'usuario',
                'espacio',
                'equipo',
                'tecnico_asignado__usuario',
                'mantenimiento',
            )
        )

    def get_all(self):
        return self._base_qs().order_by('-fecha_generado')

    def get_by_id(self, incidencia_id: int) -> Optional[Incidencia]:
        return self._base_qs().filter(id_reporte=incidencia_id).first()

    def get_by_usuario(self, usuario_id: int):
        return (
            self._base_qs()
            .filter(usuario__id_usuario=usuario_id)
            .order_by('-fecha_generado')
        )

    def get_by_estado(self, estado: str):
        return (
            self._base_qs()
            .filter(estado=estado)
            .order_by('-fecha_generado')
        )

    def get_by_espacio(self, espacio_id: int):
        return (
            self._base_qs()
            .filter(espacio__id_espacio=espacio_id)
            .order_by('-fecha_generado')
        )

    @staticmethod
    def create(**datos) -> Incidencia:
        return Incidencia.objects.create(**datos)

    @staticmethod
    def update(incidencia: Incidencia, **datos) -> Incidencia:
        for field, value in datos.items():
            setattr(incidencia, field, value)
        incidencia.save()
        return incidencia
