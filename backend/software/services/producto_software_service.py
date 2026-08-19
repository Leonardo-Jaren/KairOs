from shared.base import BaseService
from software.repositories import ProductoSoftwareRepository


class ProductoSoftwareService(BaseService):
    """Expone la consulta del catalogo de software vigente."""

    def __init__(self):
        self.repository = ProductoSoftwareRepository()

    def listar(self, busqueda: str = '', tipo_licencia: str = ''):
        """Normaliza y aplica los filtros disponibles para el catalogo."""
        return self.repository.listar(
            busqueda=busqueda.strip(),
            tipo_licencia=tipo_licencia.strip(),
        )
