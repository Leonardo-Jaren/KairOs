from software.repositories.producto_repository import ProductoSoftwareRepository
from software.models import ProductoSoftware
from software.exceptions import ProductoSoftwareNoEncontrado, DatosInvalidos


class ProductoSoftwareService:
    def __init__(self, producto_repository: ProductoSoftwareRepository):
        self.repo = producto_repository

    def listar_productos(self) -> list:
        return self.repo.get_all()

    def get_producto(self, producto_id: int) -> ProductoSoftware:
        producto = self.repo.get_by_id(producto_id)
        if producto is None:
            raise ProductoSoftwareNoEncontrado(f"Producto de software {producto_id} no encontrado")
        return producto

    def crear_producto(self, datos: dict) -> ProductoSoftware:
        software = datos.get("software", "")
        version  = datos.get("version")
        if self.repo.get_by_software_version(software, version):
            raise DatosInvalidos(f"Ya existe '{software} v{version}' en el catálogo")
        return self.repo.create(**datos)

    def actualizar_producto(self, producto_id: int, datos: dict) -> ProductoSoftware:
        producto = self.get_producto(producto_id)
        software_nuevo = datos.get("software", producto.software)
        version_nueva  = datos.get("version", producto.version)
        if software_nuevo != producto.software or version_nueva != producto.version:
            if self.repo.get_by_software_version(software_nuevo, version_nueva):
                raise DatosInvalidos(f"Ya existe '{software_nuevo} v{version_nueva}' en el catálogo")
        return self.repo.update(producto, **datos)

    def eliminar_producto(self, producto_id: int) -> None:
        producto = self.get_producto(producto_id)
        if producto.licencias_usadas > 0:
            raise DatosInvalidos(
                f"No se puede eliminar: hay {producto.licencias_usadas} instalaciones activas"
            )
        self.repo.delete(producto)
