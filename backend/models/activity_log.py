from backend.config.database import get_db_connection
from datetime import datetime
import json


class ActivityLog:
    """
    Modèle pour les logs d'activité utilisateur
    """
    
    @staticmethod
    def create(user_id, username, action, route, method, ip_address, user_agent, status_code=None, details=None):
        """
        Créer un nouveau log d'activité
        
        Args:
            user_id: ID de l'utilisateur (peut être None pour les actions non authentifiées)
            username: Nom d'utilisateur
            action: Description de l'action (ex: 'login', 'create_reservation', 'view_dashboard')
            route: Route/URL de la page
            method: Méthode HTTP (GET, POST, etc.)
            ip_address: Adresse IP de l'utilisateur
            user_agent: User agent du navigateur
            status_code: Code de statut HTTP (optionnel)
            details: Informations supplémentaires au format JSON (optionnel)
        """
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            details_json = json.dumps(details) if details else None
            
            cur.execute('''
                INSERT INTO activity_logs (
                    user_id, username, action, route, method, 
                    ip_address, user_agent, status_code, details, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                user_id,
                username,
                action,
                route,
                method,
                ip_address,
                user_agent,
                status_code,
                details_json,
                datetime.now()
            ))
            
            log_id = cur.fetchone()['id']
            conn.commit()
            return log_id
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur lors de la création du log d'activité: {e}")
            return None
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_all(limit=100, offset=0, user_id=None, action=None, start_date=None, end_date=None):
        """
        Récupérer tous les logs d'activité avec filtres optionnels
        
        Args:
            limit: Nombre maximum de logs à retourner
            offset: Décalage pour la pagination
            user_id: Filtrer par utilisateur (optionnel)
            action: Filtrer par type d'action (optionnel)
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
        """
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    al.*,
                    u.nom as user_nom,
                    u.prenom as user_prenom
                FROM activity_logs al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE 1=1
            '''
            params = []
            
            if user_id:
                query += ' AND al.user_id = %s'
                params.append(user_id)
            
            if action:
                query += ' AND al.action = %s'
                params.append(action)
            
            if start_date:
                query += ' AND al.created_at >= %s'
                params.append(start_date)
            
            if end_date:
                query += ' AND al.created_at <= %s'
                params.append(end_date)
            
            query += ' ORDER BY al.created_at DESC LIMIT %s OFFSET %s'
            params.extend([limit, offset])
            
            cur.execute(query, params)
            logs = cur.fetchall()
            return logs
            
        except Exception as e:
            print(f"Erreur lors de la récupération des logs: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_count(user_id=None, action=None, start_date=None, end_date=None):
        """
        Compter le nombre total de logs avec filtres optionnels
        """
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            query = 'SELECT COUNT(*) as count FROM activity_logs WHERE 1=1'
            params = []
            
            if user_id:
                query += ' AND user_id = %s'
                params.append(user_id)
            
            if action:
                query += ' AND action = %s'
                params.append(action)
            
            if start_date:
                query += ' AND created_at >= %s'
                params.append(start_date)
            
            if end_date:
                query += ' AND created_at <= %s'
                params.append(end_date)
            
            cur.execute(query, params)
            result = cur.fetchone()
            return result['count'] if result else 0
            
        except Exception as e:
            print(f"Erreur lors du comptage des logs: {e}")
            return 0
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_by_id(log_id):
        """
        Récupérer un log spécifique par son ID
        """
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute('''
                SELECT 
                    al.*,
                    u.nom as user_nom,
                    u.prenom as user_prenom
                FROM activity_logs al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE al.id = %s
            ''', (log_id,))
            
            log = cur.fetchone()
            return log
            
        except Exception as e:
            print(f"Erreur lors de la récupération du log: {e}")
            return None
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_user_statistics(user_id, days=30):
        """
        Obtenir des statistiques d'activité pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            days: Nombre de jours à analyser
        """
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute('''
                SELECT 
                    action,
                    COUNT(*) as count,
                    MAX(created_at) as last_action
                FROM activity_logs
                WHERE user_id = %s 
                  AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY action
                ORDER BY count DESC
            ''', (user_id, days))
            
            stats = cur.fetchall()
            return stats
            
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return []
        finally:
            cur.close()
            conn.close()
