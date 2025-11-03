from flask import Blueprint, request, jsonify
from flask_login import login_required
import os
import psycopg2
from psycopg2.extras import RealDictCursor

personnels_bp = Blueprint('personnels', __name__)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

@personnels_bp.route('/api/personnels', methods=['GET'])
@login_required
def get_personnels():
    try:
        etablissement_id = request.args.get('etablissement_id')
        actif_only = request.args.get('actif_only', 'true').lower() == 'true'
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = 'SELECT * FROM personnels'
        conditions = []
        params = []
        
        if etablissement_id:
            conditions.append('etablissement_id = %s')
            params.append(etablissement_id)
        
        if actif_only:
            conditions.append('actif = TRUE')
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY nom, prenom'
        
        cur.execute(query, params)
        personnels = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify([dict(p) for p in personnels])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@personnels_bp.route('/api/personnels/<int:personnel_id>', methods=['GET'])
@login_required
def get_personnel(personnel_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM personnels WHERE id = %s', (personnel_id,))
        personnel = cur.fetchone()
        cur.close()
        conn.close()
        
        if personnel:
            return jsonify(dict(personnel))
        return jsonify({'error': 'Personnel non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@personnels_bp.route('/api/personnels', methods=['POST'])
@login_required
def create_personnel():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO personnels (
                etablissement_id, prenom, nom, email, telephone, 
                poste, date_embauche, salaire, pages_acces, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        ''', (
            data.get('etablissement_id'),
            data.get('prenom'),
            data.get('nom'),
            data.get('email'),
            data.get('telephone'),
            data.get('poste'),
            data.get('date_embauche'),
            data.get('salaire'),
            data.get('pages_acces', []),
            data.get('actif', True)
        ))
        
        personnel = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify(dict(personnel)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@personnels_bp.route('/api/personnels/<int:personnel_id>', methods=['PUT'])
@login_required
def update_personnel(personnel_id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE personnels
            SET etablissement_id = %s, prenom = %s, nom = %s, email = %s, 
                telephone = %s, poste = %s, date_embauche = %s, salaire = %s, 
                pages_acces = %s, actif = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        ''', (
            data.get('etablissement_id'),
            data.get('prenom'),
            data.get('nom'),
            data.get('email'),
            data.get('telephone'),
            data.get('poste'),
            data.get('date_embauche'),
            data.get('salaire'),
            data.get('pages_acces', []),
            data.get('actif', True),
            personnel_id
        ))
        
        personnel = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if personnel:
            return jsonify(dict(personnel))
        return jsonify({'error': 'Personnel non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@personnels_bp.route('/api/personnels/<int:personnel_id>', methods=['DELETE'])
@login_required
def delete_personnel(personnel_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM personnels WHERE id = %s RETURNING id', (personnel_id,))
        deleted = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        if deleted:
            return jsonify({'success': True, 'message': 'Personnel supprimé'})
        return jsonify({'error': 'Personnel non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
