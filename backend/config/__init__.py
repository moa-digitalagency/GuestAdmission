"""
Configuration de l'application
"""
from .database import get_db_connection

__all__ = ['get_db_connection']
