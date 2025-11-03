from backend.config.database import get_db_connection

class Client:
    @staticmethod
    def create(data):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO clients (
                nom, prenom, mail, pays, tel, arrivee, depart, 
                sejour_numero, facture_hebergement, charge_plateforme, 
                taxe_sejour, revenu_mensuel_hebergement, 
                charges_plateforme_mensuelle, taxe_sejour_mensuelle
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('nom'), data.get('prenom'), data.get('mail'),
            data.get('pays'), data.get('tel'), data.get('arrivee'),
            data.get('depart'), data.get('sejour_numero'),
            data.get('facture_hebergement'), data.get('charge_plateforme'),
            data.get('taxe_sejour'), data.get('revenu_mensuel_hebergement'),
            data.get('charges_plateforme_mensuelle'), data.get('taxe_sejour_mensuelle')
        ))
        
        client_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        
        return client_id
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM clients ORDER BY created_at DESC')
        clients = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return clients
    
    @staticmethod
    def get_by_id(client_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM clients WHERE id = %s', (client_id,))
        client = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return client
    
    @staticmethod
    def update(client_id, data):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE clients SET
                nom = %s, prenom = %s, mail = %s, pays = %s, tel = %s,
                arrivee = %s, depart = %s, sejour_numero = %s,
                facture_hebergement = %s, charge_plateforme = %s,
                taxe_sejour = %s, revenu_mensuel_hebergement = %s,
                charges_plateforme_mensuelle = %s, taxe_sejour_mensuelle = %s
            WHERE id = %s
        ''', (
            data.get('nom'), data.get('prenom'), data.get('mail'),
            data.get('pays'), data.get('tel'), data.get('arrivee'),
            data.get('depart'), data.get('sejour_numero'),
            data.get('facture_hebergement'), data.get('charge_plateforme'),
            data.get('taxe_sejour'), data.get('revenu_mensuel_hebergement'),
            data.get('charges_plateforme_mensuelle'), data.get('taxe_sejour_mensuelle'),
            client_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def delete(client_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM clients WHERE id = %s', (client_id,))
        
        conn.commit()
        cur.close()
        conn.close()
