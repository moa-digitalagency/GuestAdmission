from backend.config.database import get_db_connection
from datetime import datetime
import json

class Newsletter:
    """Modèle pour les newsletters envoyées"""
    
    @staticmethod
    def create(etablissement_id, subject, content, content_type, recipient_emails, sent_by_user_id):
        """Créer une nouvelle newsletter"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''
                INSERT INTO newsletters (
                    etablissement_id, subject, content, content_type,
                    recipient_emails, sent_by_user_id, sent_at, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                etablissement_id, subject, content, content_type,
                json.dumps(recipient_emails), sent_by_user_id,
                datetime.now(), 'pending'
            ))
            newsletter_id = cur.fetchone()[0]
            conn.commit()
            return newsletter_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def update_status(newsletter_id, status, error_message=None):
        """Mettre à jour le statut d'une newsletter"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''
                UPDATE newsletters
                SET status = %s, error_message = %s
                WHERE id = %s
            ''', (status, error_message, newsletter_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_by_etablissement(etablissement_id, limit=50):
        """Récupérer les newsletters d'un établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT n.*, u.username, u.nom, u.prenom
                FROM newsletters n
                LEFT JOIN users u ON n.sent_by_user_id = u.id
                WHERE n.etablissement_id = %s
                ORDER BY n.sent_at DESC
                LIMIT %s
            ''', (etablissement_id, limit))
            newsletters = []
            for row in cur.fetchall():
                newsletters.append({
                    'id': row[0],
                    'etablissement_id': row[1],
                    'subject': row[2],
                    'content': row[3],
                    'content_type': row[4],
                    'recipient_emails': json.loads(row[5]) if row[5] else [],
                    'sent_by_user_id': row[6],
                    'sent_at': row[7].isoformat() if row[7] else None,
                    'status': row[8],
                    'error_message': row[9],
                    'sent_by_username': row[10],
                    'sent_by_nom': row[11],
                    'sent_by_prenom': row[12]
                })
            return newsletters
        finally:
            cur.close()
            conn.close()


class NewsletterConfig:
    """Modèle pour la configuration SendGrid de chaque établissement"""
    
    @staticmethod
    def get_by_etablissement(etablissement_id):
        """Récupérer la configuration SendGrid d'un établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT id, etablissement_id, sendgrid_api_key, from_email, from_name, active
                FROM newsletter_configs
                WHERE etablissement_id = %s AND active = true
                LIMIT 1
            ''', (etablissement_id,))
            row = cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'etablissement_id': row[1],
                    'sendgrid_api_key': row[2],
                    'from_email': row[3],
                    'from_name': row[4],
                    'active': row[5]
                }
            return None
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def create_or_update(etablissement_id, sendgrid_api_key, from_email, from_name):
        """Créer ou mettre à jour la configuration SendGrid"""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT id FROM newsletter_configs
                WHERE etablissement_id = %s
            ''', (etablissement_id,))
            existing = cur.fetchone()
            
            if existing:
                cur.execute('''
                    UPDATE newsletter_configs
                    SET sendgrid_api_key = %s, from_email = %s, from_name = %s,
                        active = true, updated_at = %s
                    WHERE etablissement_id = %s
                    RETURNING id
                ''', (sendgrid_api_key, from_email, from_name, datetime.now(), etablissement_id))
            else:
                cur.execute('''
                    INSERT INTO newsletter_configs (
                        etablissement_id, sendgrid_api_key, from_email, from_name, active
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (etablissement_id, sendgrid_api_key, from_email, from_name, True))
            
            config_id = cur.fetchone()[0]
            conn.commit()
            return config_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
