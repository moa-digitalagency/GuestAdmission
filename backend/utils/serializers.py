"""
Utilitaires pour la sérialisation des données
"""
from datetime import date, datetime
from decimal import Decimal


def serialize_row(row):
    """Convertir une ligne de base de données en dictionnaire JSON-compatible"""
    if row is None:
        return None
    
    result = {}
    for key, value in dict(row).items():
        if isinstance(value, (date, datetime)):
            result[key] = value.isoformat()
        elif isinstance(value, Decimal):
            result[key] = float(value)
        else:
            result[key] = value
    return result


def serialize_rows(rows):
    """Convertir plusieurs lignes de base de données en liste de dictionnaires"""
    if rows is None:
        return []
    return [serialize_row(row) for row in rows]
