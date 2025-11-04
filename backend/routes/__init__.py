"""
Routes de l'application
"""
from .auth import auth_bp
from .clients import clients_bp
from .sejours import sejours_bp
from .parametres import parametres_bp
from .countries import countries_bp
from .chambres import chambres_bp
from .etablissements import etablissements_bp
from .data_management import data_bp
from .personnels import personnels_bp
from .extras import extras_bp

__all__ = [
    'auth_bp',
    'clients_bp',
    'sejours_bp',
    'parametres_bp',
    'countries_bp',
    'chambres_bp',
    'etablissements_bp',
    'data_bp',
    'personnels_bp',
    'extras_bp'
]
