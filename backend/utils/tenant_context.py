"""
Utilitaires pour la gestion du contexte tenant
Fournit des helpers pour filtrer les données par tenant
"""

from flask_login import current_user
from ..config.database import get_db_connection


def get_current_tenant_id():
    """
    Obtenir l'ID du compte tenant de l'utilisateur connecté
    Retourne None si l'utilisateur est un PLATFORM_ADMIN
    """
    if not current_user.is_authenticated:
        return None
    
    if current_user.is_platform_admin():
        return None
    
    return current_user.get_tenant_account_id()


def get_accessible_etablissement_ids(user=None):
    """
    Obtenir les IDs des établissements accessibles par l'utilisateur
    
    Args:
        user: L'utilisateur (utilise current_user si non fourni)
    
    Returns:
        Liste des IDs d'établissements ou None si PLATFORM_ADMIN (tous les établissements)
    """
    if user is None:
        user = current_user
    
    if not user.is_authenticated:
        return []
    
    # PLATFORM_ADMIN a accès à tous les établissements
    if user.is_platform_admin():
        return None
    
    # Récupérer les établissements via user_etablissements
    etablissements = user.get_etablissements()
    return [etab['id'] for etab in etablissements]


def get_current_etablissement_id():
    """
    Obtenir l'ID de l'établissement courant de l'utilisateur connecté
    Retourne le premier établissement accessible pour l'utilisateur
    """
    if not current_user.is_authenticated:
        return None
    
    # Pour les PLATFORM_ADMIN, retourner None (ils doivent spécifier l'ID)
    if current_user.is_platform_admin():
        return None
    
    # Utiliser l'etablissement_id stocké dans l'user si disponible
    if hasattr(current_user, 'etablissement_id') and current_user.etablissement_id:
        return current_user.etablissement_id
    
    # Sinon, retourner le premier établissement accessible
    etablissements = current_user.get_etablissements()
    if etablissements and len(etablissements) > 0:
        return etablissements[0]['id']
    
    return None


def get_tenant_filtered_query(base_query, table_alias='e'):
    """
    Ajouter une clause WHERE pour filtrer par tenant sur une requête
    
    Args:
        base_query: La requête SQL de base
        table_alias: L'alias de la table etablissements dans la requête
    
    Returns:
        Tuple (query, params) avec la requête modifiée et les paramètres
    """
    tenant_id = get_current_tenant_id()
    
    # PLATFORM_ADMIN voit tout
    if tenant_id is None and current_user.is_platform_admin():
        return (base_query, [])
    
    # Tenant admin voit seulement son tenant
    if tenant_id:
        return (
            f"{base_query} AND {table_alias}.tenant_account_id = %s",
            [tenant_id]
        )
    
    # Utilisateurs normaux voient leurs établissements
    etablissement_ids = get_accessible_etablissement_ids()
    if etablissement_ids:
        placeholders = ','.join(['%s'] * len(etablissement_ids))
        return (
            f"{base_query} AND {table_alias}.id IN ({placeholders})",
            etablissement_ids
        )
    
    # Pas d'accès
    return (f"{base_query} AND 1=0", [])


def verify_etablissement_access(etablissement_id):
    """
    Vérifier si l'utilisateur connecté a accès à un établissement
    
    Args:
        etablissement_id: L'ID de l'établissement à vérifier
    
    Returns:
        True si l'utilisateur a accès, False sinon
    """
    if not current_user.is_authenticated:
        return False
    
    # PLATFORM_ADMIN a accès à tous les établissements
    if current_user.is_platform_admin():
        return True
    
    # Vérifier dans les établissements accessibles
    accessible_ids = get_accessible_etablissement_ids()
    if accessible_ids is None:  # PLATFORM_ADMIN
        return True
    
    return etablissement_id in accessible_ids


def verify_reservation_access(reservation_id):
    """
    Vérifier si l'utilisateur connecté a accès à une séjour
    
    Args:
        reservation_id: L'ID de la réservation à vérifier
    
    Returns:
        True si l'utilisateur a accès, False sinon
    """
    if not current_user.is_authenticated:
        return False
    
    # PLATFORM_ADMIN a accès à tout
    if current_user.is_platform_admin():
        return True
    
    # Récupérer l'etablissement_id de la séjour
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT etablissement_id 
        FROM reservations 
        WHERE id = %s
    ''', (reservation_id,))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if not result:
        return False
    
    return verify_etablissement_access(result['etablissement_id'])


def get_tenant_account_stats(tenant_id):
    """
    Obtenir les statistiques d'un compte tenant
    
    Args:
        tenant_id: L'ID du compte tenant
    
    Returns:
        Dict avec les statistiques (établissements, chambres, séjours, etc.)
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Nombre d'établissements
    cur.execute('''
        SELECT COUNT(*) as count 
        FROM etablissements 
        WHERE tenant_account_id = %s
    ''', (tenant_id,))
    nb_etablissements = cur.fetchone()['count']
    
    # Nombre de chambres
    cur.execute('''
        SELECT COUNT(*) as count 
        FROM chambres c
        INNER JOIN etablissements e ON c.etablissement_id = e.id
        WHERE e.tenant_account_id = %s
    ''', (tenant_id,))
    nb_chambres = cur.fetchone()['count']
    
    # Nombre de séjours
    cur.execute('''
        SELECT COUNT(*) as count 
        FROM reservations r
        INNER JOIN etablissements e ON r.etablissement_id = e.id
        WHERE e.tenant_account_id = %s
    ''', (tenant_id,))
    nb_sejours = cur.fetchone()['count']
    
    # Nombre d'utilisateurs
    cur.execute('''
        SELECT COUNT(DISTINCT ue.user_id) as count
        FROM user_etablissements ue
        INNER JOIN etablissements e ON ue.etablissement_id = e.id
        WHERE e.tenant_account_id = %s
    ''', (tenant_id,))
    nb_users = cur.fetchone()['count']
    
    cur.close()
    conn.close()
    
    return {
        'nb_etablissements': nb_etablissements,
        'nb_chambres': nb_chambres,
        'nb_sejours': nb_sejours,
        'nb_users': nb_users
    }
