class EquipoNoEncontrado(Exception):
    """El equipo solicitado no existe en la BD."""
    pass

class ComponenteNoEncontrado(Exception):
    """El componente solicitado no existe en la BD."""
    pass

class DatosInvalidos(Exception):
    """Violación de regla de negocio (código duplicado, estado inválido, etc.)."""
    pass
