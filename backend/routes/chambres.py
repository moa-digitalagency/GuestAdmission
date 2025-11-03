from flask import Blueprint, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

chambres_bp = Blueprint('chambres', __name__)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

@chambres_bp.route('/api/chambres', methods=['GET'])
def get_chambres():
    try:
        etablissement_id = request.args.get('etablissement_id')
        conn = get_db_connection()
        cur = conn.cursor()
        
        if etablissement_id:
            cur.execute('''
                SELECT id, etablissement_id, nom, description, capacite, prix_par_nuit, statut, created_at
                FROM chambres
                WHERE etablissement_id = %s
                ORDER BY nom
            ''', (etablissement_id,))
        else:
            cur.execute('''
                SELECT id, etablissement_id, nom, description, capacite, prix_par_nuit, statut, created_at
                FROM chambres
                ORDER BY nom
            ''')
        
        chambres = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([dict(c) for c in chambres])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres', methods=['POST'])
def create_chambre():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, etablissement_id, nom, description, capacite, prix_par_nuit, statut
        ''', (
            data.get('etablissement_id'),
            data.get('nom'),
            data.get('description', ''),
            data.get('capacite', 2),
            data.get('prix_par_nuit', 0),
            data.get('statut', 'disponible')
        ))
        
        chambre = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify(dict(chambre)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres/<int:chambre_id>', methods=['PUT'])
def update_chambre(chambre_id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE chambres
            SET nom = %s, description = %s, capacite = %s, prix_par_nuit = %s, statut = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, nom, description, capacite, prix_par_nuit, statut
        ''', (
            data.get('nom'),
            data.get('description'),
            data.get('capacite'),
            data.get('prix_par_nuit'),
            data.get('statut'),
            chambre_id
        ))
        
        chambre = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if chambre:
            return jsonify(dict(chambre))
        return jsonify({'error': 'Chambre non trouvée'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres/<int:chambre_id>', methods=['DELETE'])
def delete_chambre(chambre_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM chambres WHERE id = %s RETURNING id', (chambre_id,))
        deleted = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        if deleted:
            return jsonify({'message': 'Chambre supprimée'})
        return jsonify({'error': 'Chambre non trouvée'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres/disponibles', methods=['GET'])
def get_chambres_disponibles():
    try:
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if date_debut and date_fin:
            cur.execute('''
                SELECT c.id, c.nom, c.description, c.capacite, c.prix_par_nuit
                FROM chambres c
                WHERE c.statut = 'disponible'
                AND c.id NOT IN (
                    SELECT DISTINCT rc.chambre_id
                    FROM reservations_chambres rc
                    JOIN reservations r ON rc.reservation_id = r.id
                    WHERE r.statut != 'annulée'
                    AND (
                        (r.date_arrivee <= %s AND r.date_depart >= %s)
                        OR (r.date_arrivee <= %s AND r.date_depart >= %s)
                        OR (r.date_arrivee >= %s AND r.date_depart <= %s)
                    )
                )
                ORDER BY c.nom
            ''', (date_fin, date_debut, date_fin, date_fin, date_debut, date_fin))
        else:
            cur.execute('''
                SELECT id, nom, description, capacite, prix_par_nuit
                FROM chambres
                WHERE statut = 'disponible'
                ORDER BY nom
            ''')
        
        chambres = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify([dict(c) for c in chambres])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
