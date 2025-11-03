from ..config.database import get_db_connection
from datetime import datetime

class Reservation:
    @staticmethod
    def create(data):
        conn = get_db_connection()
        cur = conn.cursor()
        
        date_arrivee = data.get('date_arrivee')
        date_depart = data.get('date_depart')
        
        nombre_jours = None
        if date_arrivee and date_depart:
            arrivee = datetime.strptime(date_arrivee, '%Y-%m-%d')
            depart = datetime.strptime(date_depart, '%Y-%m-%d')
            nombre_jours = (depart - arrivee).days
        
        cur.execute('''
            INSERT INTO reservations (
                etablissement_id, numero_reservation, date_arrivee, date_depart, nombre_jours,
                facture_hebergement, charge_plateforme, taxe_sejour,
                revenu_mensuel_hebergement, charges_plateforme_mensuelle,
                taxe_sejour_mensuelle, statut, observations
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('etablissement_id'), data.get('numero_reservation'),
            date_arrivee, date_depart, nombre_jours,
            data.get('facture_hebergement'), data.get('charge_plateforme'),
            data.get('taxe_sejour'), data.get('revenu_mensuel_hebergement'),
            data.get('charges_plateforme_mensuelle'), data.get('taxe_sejour_mensuelle'),
            data.get('statut', 'active'), data.get('observations')
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if result:
            return result['id']
        return None
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT r.*, 
                   e.nom_etablissement,
                   p.nom as contact_nom, 
                   p.prenom as contact_prenom,
                   p.email as contact_email,
                   p.telephone as contact_telephone
            FROM reservations r
            LEFT JOIN etablissements e ON r.etablissement_id = e.id
            LEFT JOIN personnes p ON r.id = p.reservation_id AND p.est_contact_principal = TRUE
            ORDER BY r.created_at DESC
        ''')
        reservations = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return reservations
    
    @staticmethod
    def get_by_id(reservation_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM reservations WHERE id = %s', (reservation_id,))
        reservation = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return reservation
    
    @staticmethod
    def update(reservation_id, data):
        conn = get_db_connection()
        cur = conn.cursor()
        
        date_arrivee = data.get('date_arrivee')
        date_depart = data.get('date_depart')
        
        nombre_jours = None
        if date_arrivee and date_depart:
            arrivee = datetime.strptime(date_arrivee, '%Y-%m-%d')
            depart = datetime.strptime(date_depart, '%Y-%m-%d')
            nombre_jours = (depart - arrivee).days
        
        cur.execute('''
            UPDATE reservations SET
                etablissement_id = %s, numero_reservation = %s,
                date_arrivee = %s, date_depart = %s, nombre_jours = %s,
                facture_hebergement = %s, charge_plateforme = %s, taxe_sejour = %s,
                revenu_mensuel_hebergement = %s, charges_plateforme_mensuelle = %s,
                taxe_sejour_mensuelle = %s, statut = %s, observations = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (
            data.get('etablissement_id'), data.get('numero_reservation'),
            date_arrivee, date_depart, nombre_jours,
            data.get('facture_hebergement'), data.get('charge_plateforme'),
            data.get('taxe_sejour'), data.get('revenu_mensuel_hebergement'),
            data.get('charges_plateforme_mensuelle'), data.get('taxe_sejour_mensuelle'),
            data.get('statut'), data.get('observations'), reservation_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def delete(reservation_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM reservations WHERE id = %s', (reservation_id,))
        
        conn.commit()
        cur.close()
        conn.close()
