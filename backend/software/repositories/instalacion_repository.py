from typing import Optional
from software.models import SoftwareInstalado
from usuarios.repositories.base_repository import BaseRepository


class InstalacionRepository(BaseRepository[SoftwareInstalado]):
    def __init__(self):
        super().__init__(SoftwareInstalado)

    def get_all(self):
        return SoftwareInstalado.objects.select_related(
            'equipo', 'producto_software'
        ).order_by('id_instalacion')

    def get_by_id(self, instalacion_id: int) -> Optional[SoftwareInstalado]:
        return SoftwareInstalado.objects.select_related(
            'equipo', 'producto_software'
        ).filter(id_instalacion=instalacion_id).first()

    @staticmethod
    def get_by_equipo(equipo_id: int):
        return SoftwareInstalado.objects.select_related(
            'producto_software'
        ).filter(equipo__id_equipo=equipo_id)

    @staticmethod
    def get_by_producto(producto_id: int):
        return SoftwareInstalado.objects.select_related(
            'equipo'
        ).filter(producto_software__id_producto_software=producto_id)

    @staticmethod
    def existe_instalacion(equipo_id: int, producto_id: int) -> bool:
        return SoftwareInstalado.objects.filter(
            equipo__id_equipo=equipo_id,
            producto_software__id_producto_software=producto_id,
        ).exists()

    @staticmethod
    def create(**datos) -> SoftwareInstalado:
        return SoftwareInstalado.objects.create(**datos)
