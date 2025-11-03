"""
Utilitaires pour le formatage des données
"""
from datetime import datetime
from typing import Optional


def format_currency(amount: float, devise: str = 'MAD') -> str:
    """Formatter un montant en devise"""
    if amount is None:
        return '0.00'
    return f'{amount:,.2f} {devise}'


def format_date(date_str: Optional[str], format: str = '%d/%m/%Y') -> str:
    """Formatter une date"""
    if not date_str:
        return ''
    
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date_obj = date_str
        return date_obj.strftime(format)
    except:
        return str(date_str)


def format_numero_sejour(format_template: str, sequence: int) -> str:
    """Générer un numéro de séjour formaté"""
    now = datetime.now()
    numero = format_template.replace('{YYYY}', now.strftime('%Y'))
    numero = numero.replace('{MM}', now.strftime('%m'))
    numero = numero.replace('{DD}', now.strftime('%d'))
    numero = numero.replace('{NUM}', str(sequence).zfill(4))
    return numero
