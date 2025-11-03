from ..config.database import get_db_connection

class Personne:
    @staticmethod
    def create(data):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO personnes (
                reservation_id, est_contact_principal, nom, prenom, email,
                telephone, pays, type_piece_identite, numero_piece_identite,
                date_naissance
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('reservation_id'), data.get('est_contact_principal', False),
            data.get('nom'), data.get('prenom'), data.get('email'),
            data.get('telephone'), data.get('pays'), data.get('type_piece_identite'),
            data.get('numero_piece_identite'), data.get('date_naissance')
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if result:
            return result['id']  # type: ignore
        return None
    
    @staticmethod
    def get_by_reservation(reservation_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT * FROM personnes 
            WHERE reservation_id = %s 
            ORDER BY est_contact_principal DESC, id ASC
        ''', (reservation_id,))
        personnes = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return personnes
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM personnes ORDER BY created_at DESC')
        personnes = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return personnes
    
    @staticmethod
    def update(personne_id, data):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE personnes SET
                nom = %s, prenom = %s, email = %s, telephone = %s,
                pays = %s, type_piece_identite = %s, numero_piece_identite = %s,
                date_naissance = %s
            WHERE id = %s
        ''', (
            data.get('nom'), data.get('prenom'), data.get('email'),
            data.get('telephone'), data.get('pays'), data.get('type_piece_identite'),
            data.get('numero_piece_identite'), data.get('date_naissance'),
            personne_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def delete(personne_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM personnes WHERE id = %s', (personne_id,))
        
        conn.commit()
        cur.close()
        conn.close()
