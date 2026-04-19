from historial.models import Historial
from historial.repositories.historial_repository_interface import IHistoryRepository

class HistoryRepository(IHistoryRepository):
    """
    Implementación concreta del repositorio de Historial.
    Toda interacción con la base de datos ocurre aquí.
    """
    def get_all(self):
        return (
            Historial.objects
            .select_related('id_equipo_fk', 'id_mantenimiento_fk')
            .all()
        )    
    
    def get_by_id(self, id_historial: int):
        return (
            Historial.objects
            .select_related('id_equipo_fk', 'id_mantenimiento_fk')
            .filter(id_historial=id_historial)
            .first()
        )
    
    def get_by_equipo(self, id_equipo: int):
        return (
            Historial.objects
            .select_related('id_equipo_fk', 'id_mantenimiento_fk')
            .filter(id_equipo_fk=id_equipo)
        )
    
    def get_by_mantenimiento(self, id_mantenimiento: int):
        return (
            Historial.objects
            .select_related('id_equipo_fk', 'id_mantenimiento_fk')
            .filter(id_mantenimiento_fk=id_mantenimiento)
        )
    
    def create(self, data: dict):
        serializer_data = {
            'id_equipo_fk': data.get('id_equipo_fk').pk,
            'id_mantenimiento_fk_id': data.get('id_mantenimiento_fk').pk 
                                    if data.get('id_mantenimiento_fk') else None,
            'fecha': data.get('fecha'),                       
            'descripcion': data.get('descripcion'),
        }
        return Historial.objects.create(**serializer_data)
    
    def update(self, id_historial: int, data: dict):
        historial = self.get_by_id(id_historial)
        if not historial:
            return None
        for field, value in data.items():
            setattr(historial, field, value)
        historial.save()
        return historial

    def delete(self, id_historial: int) -> bool:
        Historial = self.get_by_id(id_historial)
        if not Historial:
            return False
        Historial.delete()
        return True     