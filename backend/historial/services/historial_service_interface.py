from abc import ABC, abstractmethod

class IHistorialService(ABC):
    """
    Interfaz del servicio de Historial.
    Define las operaciones de negocio disponibles.
    """
    @abstractmethod 
    def listar_historiales(self):
        """Retorna todos los registros de historial."""
        raise NotImplementedError

    @abstractmethod
    def obtener_historial(self, id_historial: int):
        """Obtiene el historial por su ID."""
        raise NotImplementedError
    
    @abstractmethod
    def listar_por_equipo(self, id_mantenimiento: int):
        """Retorna el historial asociado a un mantenimiento."""
        raise NotImplementedError
    
    @abstractmethod
    def listar_por_mantenimiento(self, id_mantenimiento: int):
        """Retorna el historial asociado a un mantenimiento."""
        raise NotImplementedError
    
    @abstractmethod
    def crear_historial(self, data: dict):
        """Valida y crea un nuevo registro de historial."""
        raise NotImplementedError
    
    @abstractmethod
    def actualizar_historial(self, id_historial: int, data: dict):
        """Valida y actualiza un registro de historial existente."""
        raise NotImplementedError
    
    @abstractmethod
    def eliminar_historial(self, id_historial: int)-> bool:
        """Elimina un registro. Lanza excepción si no existe."""
        raise NotImplementedError