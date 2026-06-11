from mantenimiento.models import TecnicoMantenimiento
from usuarios.repositories.base_repository import BaseRepository


class TecnicoMantenimientoRepository(BaseRepository[TecnicoMantenimiento]):

    def __init__(self):
        super().__init__(TecnicoMantenimiento)

    @staticmethod
    def get_by_mantenimiento(mantenimiento_id: int):
        return (
            TecnicoMantenimiento.objects
            .select_related('tecnico__usuario')
            .filter(mantenimiento__id_mantenimiento=mantenimiento_id)
        )

    @staticmethod
    def existe_asignacion(mantenimiento_id: int, tecnico_id: int) -> bool:
        return TecnicoMantenimiento.objects.filter(
            mantenimiento__id_mantenimiento=mantenimiento_id,
            tecnico__id_tecnico=tecnico_id,
        ).exists()

    @staticmethod
    def crear_asignacion(mantenimiento, tecnico) -> TecnicoMantenimiento:
        return TecnicoMantenimiento.objects.create(
            mantenimiento=mantenimiento,
            tecnico=tecnico,
        )

    @staticmethod
    def eliminar_asignacion(mantenimiento_id: int, tecnico_id: int) -> bool:
        deleted, _ = TecnicoMantenimiento.objects.filter(
            mantenimiento__id_mantenimiento=mantenimiento_id,
            tecnico__id_tecnico=tecnico_id,
        ).delete()
        return deleted > 0
