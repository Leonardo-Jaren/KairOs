from historial.repositories.historial_repository import HistorialRepository
from historial.models import Historial
from historial.exceptions import RegistroNoEncontrado


class HistorialService:
    """
    SRP — sólo expone consultas sobre el log de auditoría.
    DIP — depende de HistorialRepository, no de la implementación concreta.

    No existe ningún método de escritura: el historial es inmutable desde
    el punto de vista de la aplicación; sólo PostgreSQL lo escribe.
    """

    def __init__(self, historial_repository: HistorialRepository):
        self.repo = historial_repository

    def listar_historial(
        self,
        tabla:       str = None,
        registro_id: int = None,
        usuario_id:  int = None,
        accion:      str = None,
        fecha_desde       = None,
        fecha_hasta       = None,
    ) -> list:
        return self.repo.filtrar(
            tabla=tabla,
            registro_id=registro_id,
            usuario_id=usuario_id,
            accion=accion,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

    def get_registro(self, historial_id: int) -> Historial:
        registro = self.repo.get_by_id(historial_id)
        if registro is None:
            raise RegistroNoEncontrado(
                f"Registro de historial {historial_id} no encontrado"
            )
        return registro
