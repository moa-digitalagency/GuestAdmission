from functools import wraps
from flask import jsonify
from flask_login import current_user

def platform_admin_required(f):
    """Décorateur pour protéger les routes nécessitant le rôle PLATFORM_ADMIN"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Non authentifié'}), 401
        
        if not current_user.is_platform_admin():
            return jsonify({'error': 'Accès refusé. Rôle PLATFORM_ADMIN requis.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Décorateur pour protéger les routes nécessitant le rôle SUPER_ADMIN (alias pour platform_admin_required)"""
    # Garde la compatibilité avec l'ancien code
    return platform_admin_required(f)

def tenant_admin_required(f):
    """Décorateur pour protéger les routes nécessitant le rôle admin (tenant admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Non authentifié'}), 401
        
        if not current_user.is_admin():
            return jsonify({'error': 'Accès refusé. Rôle admin requis.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def admin_or_super_admin_required(f):
    """Décorateur pour protéger les routes nécessitant le rôle admin ou SUPER_ADMIN"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Non authentifié'}), 401
        
        if not (current_user.is_admin() or current_user.is_super_admin()):
            return jsonify({'error': 'Accès refusé. Rôle admin requis.'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def can_manage_etablissement(etablissement_id_param='etablissement_id'):
    """Décorateur pour vérifier si l'utilisateur peut gérer un établissement"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Non authentifié'}), 401
            
            etablissement_id = kwargs.get(etablissement_id_param)
            
            if not etablissement_id:
                return jsonify({'error': 'ID établissement manquant'}), 400
            
            if not current_user.can_manage_etablissement(etablissement_id):
                return jsonify({'error': 'Accès refusé à cet établissement'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
