from abc import ABC, abstractmethod

class IHistoryRepository(ABC):
    """
    Interfaz del repositorio de Historial.
    Define el contrato que debe cumplir cualquier implementación concreta.
    """
    @abstractmethod
    def get_all(self):
        """Retorna todos los registros de historial.""" 
        raise NotImplementedError 
    
    @abstractmethod
    def get_by_equipo(self, id_equipo: int):
        """Retorna todos los historiales de un equipo específico."""
        raise NotImplementedError
    
    @abstractmethod
    def get_by_mantenimiento(self, id_mantenimiento: int):
        """Retorna el historial asociado a un mantenimiento específico."""
        raise NotImplementedError
    
    @abstractmethod
    def create(self, data: dict):
        """Crea y retorna un nuevo registro de historial."""
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, id_historial: int) -> bool:
        """Elimina un registro. Retorna True si tuvo éxito."""
        raise NotImplementedError