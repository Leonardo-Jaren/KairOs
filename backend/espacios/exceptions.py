class PabellonNoEncontrado(Exception):
    """El pabellón solicitado no existe en la BD."""
    pass

class EspacioNoEncontrado(Exception):
    """El espacio solicitado no existe en la BD."""
    pass

class DatosInvalidos(Exception):
    """Violación de regla de negocio (código duplicado, etc.)."""
    pass
