from software.repositories.instalacion_repository import InstalacionRepository
from software.repositories.producto_repository import ProductoSoftwareRepository
from software.models import SoftwareInstalado
from software.exceptions import InstalacionNoEncontrada, ProductoSoftwareNoEncontrado, DatosInvalidos


class InstalacionService:
    def __init__(
        self,
        instalacion_repository: InstalacionRepository,
        producto_repository: ProductoSoftwareRepository,
    ):
        self.repo         = instalacion_repository
        self.producto_repo = producto_repository

    def listar_instalaciones(self, equipo_id: int = None, producto_id: int = None) -> list:
        if equipo_id is not None:
            return self.repo.get_by_equipo(equipo_id)
        if producto_id is not None:
            return self.repo.get_by_producto(producto_id)
        return self.repo.get_all()

    def instalar_software(self, datos: dict) -> SoftwareInstalado:
        """
        Reglas de negocio antes de instalar:
        1. No instalar el mismo software dos veces en el mismo equipo.
        2. Verificar que haya licencias disponibles.
        """
        equipo_id   = datos["equipo"].id_equipo
        producto_id = datos["producto_software"].id_producto_software

        if self.repo.existe_instalacion(equipo_id, producto_id):
            raise DatosInvalidos("Este software ya está instalado en el equipo")

        producto = self.producto_repo.get_by_id(producto_id)
        if producto is None:
            raise ProductoSoftwareNoEncontrado("Producto de software no encontrado")

        if producto.licencias_disponibles <= 0:
            raise DatosInvalidos(
                f"Sin licencias disponibles para '{producto.software}'. "
                f"Usadas: {producto.licencias_usadas} / Total: {producto.licencias_totales}"
            )

        return self.repo.create(**datos)

    def desinstalar_software(self, instalacion_id: int) -> None:
        instalacion = self.repo.get_by_id(instalacion_id)
        if instalacion is None:
            raise InstalacionNoEncontrada(f"Instalación {instalacion_id} no encontrada")
        self.repo.delete(instalacion)
