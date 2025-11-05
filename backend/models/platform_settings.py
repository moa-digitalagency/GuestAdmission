from ..config.database import get_db_connection


class PlatformSettings:
    """Modèle pour les paramètres globaux de la plateforme"""
    
    @staticmethod
    def get_settings():
        """Récupérer les paramètres de la plateforme"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM platform_settings ORDER BY id LIMIT 1')
        settings = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return settings
    
    @staticmethod
    def update_settings(data):
        """Mettre à jour les paramètres de la plateforme"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE platform_settings SET
                platform_name = %s,
                platform_logo_url = %s,
                support_email = %s,
                support_phone = %s,
                default_currency = %s,
                default_language = %s,
                maintenance_mode = %s,
                maintenance_message = %s,
                custom_css = %s,
                custom_js = %s,
                meta_title = %s,
                meta_description = %s,
                meta_keywords = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM platform_settings ORDER BY id LIMIT 1)
        ''', (
            data.get('platform_name'),
            data.get('platform_logo_url'),
            data.get('support_email'),
            data.get('support_phone'),
            data.get('default_currency'),
            data.get('default_language'),
            data.get('maintenance_mode', False),
            data.get('maintenance_message'),
            data.get('custom_css'),
            data.get('custom_js'),
            data.get('meta_title'),
            data.get('meta_description'),
            data.get('meta_keywords')
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def get_public_settings():
        """Récupérer uniquement les paramètres publics (nom, logo, etc.)"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT 
                platform_name,
                platform_logo_url,
                default_currency,
                default_language,
                maintenance_mode,
                maintenance_message,
                meta_title,
                meta_description,
                meta_keywords
            FROM platform_settings 
            ORDER BY id LIMIT 1
        ''')
        settings = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return settings
