import logging


def get_logger(name: str) -> logging.Logger:
    """
    Retorna un logger nombrado configurado por Django.
    Uso: logger = get_logger(__name__)
    """
    return logging.getLogger(name)
