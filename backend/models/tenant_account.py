from ..config.database import get_db_connection

class TenantAccount:
    """Modèle pour les comptes clients (tenants) dans le système SaaS"""
    
    @staticmethod
    def create(nom_compte, primary_admin_user_id=None, notes=''):
        """Créer un nouveau compte tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO tenant_accounts (nom_compte, primary_admin_user_id, notes)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', (nom_compte, primary_admin_user_id, notes))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return result['id'] if result else None
    
    @staticmethod
    def get_by_id(tenant_id):
        """Obtenir un compte tenant par son ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM tenant_accounts WHERE id = %s', (tenant_id,))
        tenant = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return tenant
    
    @staticmethod
    def get_all(actif_only=True):
        """Obtenir tous les comptes tenants"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        if actif_only:
            cur.execute('SELECT * FROM tenant_accounts WHERE actif = TRUE ORDER BY nom_compte')
        else:
            cur.execute('SELECT * FROM tenant_accounts ORDER BY nom_compte')
        
        tenants = cur.fetchall()
        cur.close()
        conn.close()
        
        return tenants
    
    @staticmethod
    def update(tenant_id, data):
        """Mettre à jour un compte tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE tenant_accounts SET
                nom_compte = %s,
                primary_admin_user_id = %s,
                notes = %s,
                actif = %s
            WHERE id = %s
        ''', (
            data.get('nom_compte'),
            data.get('primary_admin_user_id'),
            data.get('notes', ''),
            data.get('actif', True),
            tenant_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def delete(tenant_id):
        """Supprimer un compte tenant (soft delete)"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('UPDATE tenant_accounts SET actif = FALSE WHERE id = %s', (tenant_id,))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def get_etablissements(tenant_id):
        """Obtenir tous les établissements d'un compte tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT * FROM etablissements 
            WHERE tenant_account_id = %s 
            ORDER BY nom_etablissement
        ''', (tenant_id,))
        
        etablissements = cur.fetchall()
        cur.close()
        conn.close()
        
        return etablissements
    
    @staticmethod
    def get_stats(tenant_id):
        """Obtenir les statistiques d'un compte tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Nombre d'établissements
        cur.execute('SELECT COUNT(*) as count FROM etablissements WHERE tenant_account_id = %s', (tenant_id,))
        nb_etablissements = cur.fetchone()['count']
        
        # Nombre de chambres total
        cur.execute('''
            SELECT COUNT(*) as count FROM chambres c
            INNER JOIN etablissements e ON c.etablissement_id = e.id
            WHERE e.tenant_account_id = %s
        ''', (tenant_id,))
        nb_chambres = cur.fetchone()['count']
        
        # Nombre de séjours total
        cur.execute('''
            SELECT COUNT(*) as count FROM reservations r
            INNER JOIN etablissements e ON r.etablissement_id = e.id
            WHERE e.tenant_account_id = %s
        ''', (tenant_id,))
        nb_sejours = cur.fetchone()['count']
        
        cur.close()
        conn.close()
        
        return {
            'nb_etablissements': nb_etablissements,
            'nb_chambres': nb_chambres,
            'nb_sejours': nb_sejours
        }
