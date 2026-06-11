from typing import Optional
from mantenimiento.models import Mantenimiento
from usuarios.repositories.base_repository import BaseRepository


class MantenimientoRepository(BaseRepository[Mantenimiento]):

    def __init__(self):
        super().__init__(Mantenimiento)

    def get_all(self):
        return (
            Mantenimiento.objects
            .select_related('equipo', 'usuario_cierre')
            .prefetch_related('tecnicos_asignados__tecnico__usuario')
            .order_by('-fecha_inicio')
        )

    def get_by_id(self, mantenimiento_id: int) -> Optional[Mantenimiento]:
        return (
            Mantenimiento.objects
            .select_related('equipo', 'usuario_cierre')
            .prefetch_related('tecnicos_asignados__tecnico__usuario')
            .filter(id_mantenimiento=mantenimiento_id)
            .first()
        )

    def get_by_equipo(self, equipo_id: int):
        return (
            Mantenimiento.objects
            .select_related('equipo', 'usuario_cierre')
            .prefetch_related('tecnicos_asignados__tecnico__usuario')
            .filter(equipo__id_equipo=equipo_id)
            .order_by('-fecha_inicio')
        )

    def get_pendientes(self):
        return (
            Mantenimiento.objects
            .select_related('equipo', 'usuario_cierre')
            .prefetch_related('tecnicos_asignados__tecnico__usuario')
            .filter(estado=Mantenimiento.Estado.PENDIENTE)
            .order_by('-fecha_inicio')
        )

    @staticmethod
    def create(**datos) -> Mantenimiento:
        return Mantenimiento.objects.create(**datos)

    @staticmethod
    def update(mantenimiento: Mantenimiento, **datos) -> Mantenimiento:
        for field, value in datos.items():
            setattr(mantenimiento, field, value)
        mantenimiento.save()
        return mantenimiento
