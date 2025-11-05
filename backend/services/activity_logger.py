from flask import request
from flask_login import current_user
from functools import wraps
from backend.models.activity_log import ActivityLog


def get_client_ip():
    """
    Obtenir l'adresse IP réelle du client en tenant compte des proxys
    """
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    return ip


def log_activity(action, details=None):
    """
    Enregistrer une activité utilisateur
    
    Args:
        action: Type d'action (ex: 'login', 'create_sejour', 'update_client')
        details: Informations supplémentaires (dict, sera converti en JSON)
    """
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        username = current_user.username if current_user.is_authenticated else 'Anonymous'
        
        ip_address = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')[:500]
        route = request.path
        method = request.method
        
        ActivityLog.create(
            user_id=user_id,
            username=username,
            action=action,
            route=route,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'activité: {e}")


def track_activity(action_name):
    """
    Décorateur pour enregistrer automatiquement une activité lors de l'appel d'une fonction
    
    Usage:
        @track_activity('create_sejour')
        def create_sejour():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            log_activity(action_name)
            return result
        return decorated_function
    return decorator


class ActivityLoggerMiddleware:
    """
    Middleware pour enregistrer automatiquement toutes les requêtes
    """
    
    def __init__(self, app):
        self.app = app
        
        @app.after_request
        def log_request(response):
            """
            Enregistrer chaque requête après son traitement
            """
            try:
                if request.path.startswith('/static/'):
                    return response
                
                if request.path == '/favicon.ico':
                    return response
                
                user_id = current_user.id if current_user.is_authenticated else None
                username = current_user.username if current_user.is_authenticated else 'Anonymous'
                
                action = self._determine_action(request.method, request.path)
                
                ip_address = get_client_ip()
                user_agent = request.headers.get('User-Agent', '')[:500]
                
                details = None
                if request.method == 'POST' and request.path not in ['/auth/login', '/auth/register']:
                    details = {
                        'form_data': list(request.form.keys()) if request.form else [],
                        'query_params': dict(request.args)
                    }
                
                ActivityLog.create(
                    user_id=user_id,
                    username=username,
                    action=action,
                    route=request.path,
                    method=request.method,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status_code=response.status_code,
                    details=details
                )
            except Exception as e:
                print(f"Erreur dans ActivityLoggerMiddleware: {e}")
            
            return response
    
    @staticmethod
    def _determine_action(method, path):
        """
        Déterminer le type d'action basé sur la méthode et le chemin
        """
        path_lower = path.lower()
        
        if '/auth/login' in path_lower:
            return 'login'
        elif '/auth/logout' in path_lower:
            return 'logout'
        elif '/dashboard' in path_lower:
            return 'view_dashboard'
        elif '/nouveau-sejour' in path_lower:
            return 'view_new_sejour_form'
        elif '/sejours' in path_lower and method == 'GET':
            return 'view_sejours_list'
        elif '/sejours' in path_lower and method == 'POST':
            return 'create_sejour'
        elif '/sejour/' in path_lower and method == 'GET':
            return 'view_sejour_detail'
        elif '/clients' in path_lower and method == 'GET':
            return 'view_clients_list'
        elif '/clients' in path_lower and method == 'POST':
            return 'create_client'
        elif '/parametres' in path_lower:
            return 'view_settings'
        elif '/statistiques' in path_lower:
            return 'view_statistics'
        elif '/extras' in path_lower:
            return 'view_extras'
        elif '/messagerie' in path_lower:
            return 'view_messages'
        elif '/calendriers' in path_lower:
            return 'view_calendars'
        elif method == 'POST':
            return 'create_or_update'
        elif method == 'DELETE':
            return 'delete'
        elif method == 'PUT' or method == 'PATCH':
            return 'update'
        else:
            return 'view_page'
