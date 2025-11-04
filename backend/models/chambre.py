from ..config.database import get_db_connection

class Chambre:
    @staticmethod
    def create(data):
        """Créer une nouvelle chambre"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('etablissement_id'),
            data.get('nom'),
            data.get('description', ''),
            data.get('capacite', 2),
            data.get('prix_par_nuit', 0),
            data.get('statut', 'disponible')
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return result['id'] if result else None
    
    @staticmethod
    def get_by_id(chambre_id):
        """Obtenir une chambre par son ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM chambres WHERE id = %s', (chambre_id,))
        chambre = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return chambre
    
    @staticmethod
    def get_by_etablissement(etablissement_id):
        """Obtenir toutes les chambres d'un établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT * FROM chambres 
            WHERE etablissement_id = %s 
            ORDER BY nom
        ''', (etablissement_id,))
        
        chambres = cur.fetchall()
        cur.close()
        conn.close()
        
        return chambres
    
    @staticmethod
    def get_all():
        """Obtenir toutes les chambres"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM chambres ORDER BY nom')
        chambres = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return chambres
    
    @staticmethod
    def update(chambre_id, data):
        """Mettre à jour une chambre"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE chambres SET
                nom = %s,
                description = %s,
                capacite = %s,
                prix_par_nuit = %s,
                statut = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (
            data.get('nom'),
            data.get('description'),
            data.get('capacite'),
            data.get('prix_par_nuit'),
            data.get('statut'),
            chambre_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def delete(chambre_id):
        """Supprimer une chambre"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM chambres WHERE id = %s', (chambre_id,))
        
        conn.commit()
        cur.close()
        conn.close()
