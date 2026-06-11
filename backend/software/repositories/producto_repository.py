from typing import Optional
from software.models import ProductoSoftware
from usuarios.repositories.base_repository import BaseRepository


class ProductoSoftwareRepository(BaseRepository[ProductoSoftware]):
    def __init__(self):
        super().__init__(ProductoSoftware)

    def get_all(self):
        return ProductoSoftware.objects.all().order_by('software', 'version')

    def get_by_id(self, producto_id: int) -> Optional[ProductoSoftware]:
        return ProductoSoftware.objects.filter(id_producto_software=producto_id).first()

    @staticmethod
    def get_by_software_version(software: str, version: str) -> Optional[ProductoSoftware]:
        return ProductoSoftware.objects.filter(software=software, version=version).first()

    @staticmethod
    def create(**datos) -> ProductoSoftware:
        return ProductoSoftware.objects.create(**datos)

    @staticmethod
    def update(producto: ProductoSoftware, **datos) -> ProductoSoftware:
        for field, value in datos.items():
            setattr(producto, field, value)
        producto.save()
        return producto
