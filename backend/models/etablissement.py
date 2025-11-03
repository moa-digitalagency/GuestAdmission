from ..config.database import get_db_connection

class Etablissement:
    @staticmethod
    def create(data):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO etablissements (
                nom_etablissement, numero_identification, pays, ville, adresse,
                telephone, whatsapp, email, devise, taux_taxe_sejour,
                taux_tva, taux_charge_plateforme, logo_url,
                format_numero_reservation, actif
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('nom_etablissement'), data.get('numero_identification'),
            data.get('pays'), data.get('ville'), data.get('adresse'),
            data.get('telephone'), data.get('whatsapp'), data.get('email'),
            data.get('devise', 'MAD'), data.get('taux_taxe_sejour'),
            data.get('taux_tva'), data.get('taux_charge_plateforme'),
            data.get('logo_url'), data.get('format_numero_reservation', 'RES-{YYYY}{MM}{DD}-{NUM}'),
            data.get('actif', True)
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if result:
            return result['id']
        return None
    
    @staticmethod
    def get_all(actif_only=True):
        conn = get_db_connection()
        cur = conn.cursor()
        
        if actif_only:
            cur.execute('SELECT * FROM etablissements WHERE actif = TRUE ORDER BY nom_etablissement')
        else:
            cur.execute('SELECT * FROM etablissements ORDER BY nom_etablissement')
        
        etablissements = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return etablissements
    
    @staticmethod
    def get_by_id(etablissement_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM etablissements WHERE id = %s', (etablissement_id,))
        etablissement = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return etablissement
    
    @staticmethod
    def update(etablissement_id, data):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE etablissements SET
                nom_etablissement = %s, numero_identification = %s,
                pays = %s, ville = %s, adresse = %s,
                telephone = %s, whatsapp = %s, email = %s,
                devise = %s, taux_taxe_sejour = %s, taux_tva = %s,
                taux_charge_plateforme = %s, logo_url = %s,
                format_numero_reservation = %s, actif = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (
            data.get('nom_etablissement'), data.get('numero_identification'),
            data.get('pays'), data.get('ville'), data.get('adresse'),
            data.get('telephone'), data.get('whatsapp'), data.get('email'),
            data.get('devise'), data.get('taux_taxe_sejour'), data.get('taux_tva'),
            data.get('taux_charge_plateforme'), data.get('logo_url'),
            data.get('format_numero_reservation'), data.get('actif', True),
            etablissement_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def delete(etablissement_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM etablissements WHERE id = %s', (etablissement_id,))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def generer_numero_reservation(etablissement_id):
        from datetime import datetime
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT format_numero_reservation, prochain_numero_sequence 
            FROM etablissements 
            WHERE id = %s
        ''', (etablissement_id,))
        
        result = cur.fetchone()
        
        if result:
            format_str = result['format_numero_reservation'] or 'RES-{YYYY}{MM}{DD}-{NUM}'
            numero_seq = result['prochain_numero_sequence'] or 1
            
            now = datetime.now()
            numero = format_str.replace('{YYYY}', now.strftime('%Y'))
            numero = numero.replace('{MM}', now.strftime('%m'))
            numero = numero.replace('{DD}', now.strftime('%d'))
            numero = numero.replace('{NUM}', str(numero_seq).zfill(4))
            
            cur.execute('''
                UPDATE etablissements 
                SET prochain_numero_sequence = prochain_numero_sequence + 1
                WHERE id = %s
            ''', (etablissement_id,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return numero
        
        cur.close()
        conn.close()
        return None
