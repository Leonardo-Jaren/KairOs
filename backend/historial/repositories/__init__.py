# historial/repositories
# TODO: Implementar repositorios para Historial
# historial/repositories/__init__.py

from .historial_repository import HistorialRepository
from .historial_repository_interface import IHistorialRepository

__all__ = ['HistorialRepository', 'IHistorialRepository']