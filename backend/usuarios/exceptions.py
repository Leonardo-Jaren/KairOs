class AutenticacionError(Exception):
    """Credenciales invalidas, usuario inactivo, token expirado"""
    pass

class UsuarioNoEncontrado(Exception):
    """El usuario solicitado no existe en la BD"""
    pass

class DatosInvalidos(Exception):
    """Violacion de regla de negocio (correo duplicado, etc)"""
    pass