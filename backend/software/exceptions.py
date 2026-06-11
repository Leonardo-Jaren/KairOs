class ProductoSoftwareNoEncontrado(Exception):
    """El producto de software solicitado no existe en la BD."""
    pass

class InstalacionNoEncontrada(Exception):
    """La instalación solicitada no existe en la BD."""
    pass

class DatosInvalidos(Exception):
    """Violación de regla de negocio (sin licencias, ya instalado, etc.)."""
    pass
