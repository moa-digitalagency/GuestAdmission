"""
Modèle pour la gestion des configurations mail
"""
from ..config.database import get_db_connection
from typing import Optional, Dict, List


class MailConfig:
    """Gestion des configurations mail SMTP/POP"""
    
    @staticmethod
    def create(data: Dict) -> int:
        """Créer une nouvelle configuration mail"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO mail_configs (
                etablissement_id, nom_config, email_address,
                smtp_host, smtp_port, smtp_username, smtp_password, smtp_use_tls,
                pop_host, pop_port, pop_username, pop_password, pop_use_ssl,
                actif
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('etablissement_id'),
            data.get('nom_config'),
            data.get('email_address'),
            data.get('smtp_host'),
            data.get('smtp_port', 587),
            data.get('smtp_username'),
            data.get('smtp_password'),
            data.get('smtp_use_tls', True),
            data.get('pop_host'),
            data.get('pop_port', 995),
            data.get('pop_username'),
            data.get('pop_password'),
            data.get('pop_use_ssl', True),
            data.get('actif', True)
        ))
        
        config_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        
        return config_id
    
    @staticmethod
    def get_all(etablissement_id: Optional[int] = None) -> List[Dict]:
        """Récupérer toutes les configurations mail"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        if etablissement_id:
            cur.execute('''
                SELECT * FROM mail_configs 
                WHERE etablissement_id = %s 
                ORDER BY created_at DESC
            ''', (etablissement_id,))
        else:
            cur.execute('SELECT * FROM mail_configs ORDER BY created_at DESC')
        
        configs = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(config) for config in configs] if configs else []
    
    @staticmethod
    def get_by_id(config_id: int) -> Optional[Dict]:
        """Récupérer une configuration par ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM mail_configs WHERE id = %s', (config_id,))
        config = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(config) if config else None
    
    @staticmethod
    def update(config_id: int, data: Dict):
        """Mettre à jour une configuration mail"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE mail_configs SET
                nom_config = %s,
                email_address = %s,
                smtp_host = %s,
                smtp_port = %s,
                smtp_username = %s,
                smtp_password = %s,
                smtp_use_tls = %s,
                pop_host = %s,
                pop_port = %s,
                pop_username = %s,
                pop_password = %s,
                pop_use_ssl = %s,
                actif = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (
            data.get('nom_config'),
            data.get('email_address'),
            data.get('smtp_host'),
            data.get('smtp_port'),
            data.get('smtp_username'),
            data.get('smtp_password'),
            data.get('smtp_use_tls'),
            data.get('pop_host'),
            data.get('pop_port'),
            data.get('pop_username'),
            data.get('pop_password'),
            data.get('pop_use_ssl'),
            data.get('actif'),
            config_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def delete(config_id: int):
        """Supprimer une configuration mail"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM mail_configs WHERE id = %s', (config_id,))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def get_active_configs(etablissement_id: Optional[int] = None) -> List[Dict]:
        """Récupérer les configurations mail actives"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        if etablissement_id:
            cur.execute('''
                SELECT * FROM mail_configs 
                WHERE etablissement_id = %s AND actif = TRUE
                ORDER BY created_at DESC
            ''', (etablissement_id,))
        else:
            cur.execute('''
                SELECT * FROM mail_configs 
                WHERE actif = TRUE 
                ORDER BY created_at DESC
            ''')
        
        configs = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(config) for config in configs] if configs else []
