from decimal import Decimal
from datetime import date, datetime

def serialize_decimal(obj):
    """
    Convertit les objets Decimal, date et datetime en types sérialisables JSON
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj

def serialize_row(row):
    """
    Convertit une ligne de résultat de base de données en dictionnaire sérialisable
    """
    if row is None:
        return None
    return {key: serialize_decimal(value) for key, value in dict(row).items()}

def serialize_rows(rows):
    """
    Convertit une liste de lignes en liste de dictionnaires sérialisables
    """
    return [serialize_row(row) for row in rows]
