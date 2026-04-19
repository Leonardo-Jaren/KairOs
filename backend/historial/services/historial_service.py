from django.core.exceptions import ObjectDoesNotExist

from historial.repositories.historial_repository_interface import IHistorialRepository
from historial.services.historial_service_interface import IHistorialService

class HistorialService(IHistorialService):
    """
    Implementación concreta del servicio de Historial.
    Contiene la lógica de negocio y delega el acceso a datos al repositorio.
    """
    def __init__(self, repository: IHistorialRepository): 
        self.repository = repository

 # ── Lectura ──────────────────────────────────────────────────────────────

    def listar_historial(self):
        return self._repository.get_all()

    def obtener_historial(self, id_historial: int):
        historial = self._repository.get_by_id(id_historial)
        if not historial:
            raise ObjectDoesNotExist(
                f"No se encontró el historial con ID {id_historial}."
            )         
        return historial
    
    def listar_por_equipo(self, id_equipo: int):
        resultados = self._repository.get_by_equipo(id_equipo)
        if not resultados:
            raise ObjectDoesNotExist(
                f"No se encontraron historiales para el equipo con ID {id_equipo}."
            )
        return resultados
    
    def listar_por_mantenimiento(self, id_mantenimiento: int):
        resultado = self._repository.get_by_mantenimiento(id_mantenimiento)
        if not resultado.exists():
            raise ObjectDoesNotExist(
                f"No se encontraron historiales para el mantenimiento con ID {id_mantenimiento}."
            )
        return resultado
    
# ── Escritura ─────────────────────────────────────────────────────────────    

    def crear_historial(self, data: dict):
        self._validar_datos(data)
        return self._repository.create(data)

    def actualizar_historial(self, id_historial: int, data: dict):
        self._obtener_historial(id_historial)
        self._validar_data_parcial(data)
        return self._repository.update(id_historial, data)

    def eliminar_historial(self, id_historial: int) -> bool:
        # Verifica que el registro exista antes de eliminar
        self.obtener_historial(id_historial)
        return self._repository.delete(id_historial)

# ── Validaciones internas (privadas) ──────────────────────────────────────
    
    def _validar_data_parcial(self, data: dict):
        """Validaciones de negocio para creación o actualización de historial."""
        if not data.get('id_equipo_fk'):
            raise ValueError("El equipo es obligatorio para registrar un historial.")

        if not data.get('fecha'):
            raise ValueError("La fecha es obligatoria.") 
        
        descripcion = data.get('descripcion', '').strip()
        if not descripcion:
            raise ValueError("La descripción del evento no puede estar vacía.") 

    def _validar_data_parcial(self, data: dict):
        """Validaciones de negocio para actualización parcial."""
        if 'descripcion' in data:
            if not data['descripcion'] or not data['descripcion'].strip():
                raise ValueError("La descripción no puede quedar vacía.")
            
        if 'id_equipo_fk' in data and not data['id_equipo_fk']:
            raise ValueError("El equipo no puede ser vacío.")    
         