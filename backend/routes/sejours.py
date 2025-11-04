from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..models.reservation import Reservation
from ..models.personne import Personne
from ..utils import serialize_rows, serialize_row
from ..config.database import get_db_connection
from datetime import datetime

sejours_bp = Blueprint('sejours', __name__)

@sejours_bp.route('/api/sejours', methods=['GET'])
@login_required
def get_sejours():
    sejours = Reservation.get_all()
    return jsonify(serialize_rows(sejours))

@sejours_bp.route('/api/sejours/<int:sejour_id>', methods=['GET'])
@login_required
def get_sejour(sejour_id):
    sejour = Reservation.get_by_id(sejour_id)
    if sejour:
        personnes = Personne.get_by_reservation(sejour_id)
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT c.id, c.nom, c.description, c.capacite
            FROM chambres c
            JOIN reservations_chambres rc ON c.id = rc.chambre_id
            WHERE rc.reservation_id = %s
        ''', (sejour_id,))
        chambres = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'sejour': serialize_row(sejour),
            'personnes': serialize_rows(personnes),
            'chambres': [dict(c) for c in chambres] if chambres else []
        })
    return jsonify({'error': 'Séjour non trouvé'}), 404

@sejours_bp.route('/api/sejours/generer-numero', methods=['GET'])
@login_required
def generer_numero_sejour():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT format_numero_reservation, prochain_numero_sequence FROM parametres_systeme LIMIT 1')
        params = cur.fetchone()
        
        if params:
            format_str = params['format_numero_reservation'] or 'RES-{YYYY}{MM}{DD}-{NUM}'
            numero_seq = params['prochain_numero_sequence'] or 1
            
            now = datetime.now()
            numero = format_str.replace('{YYYY}', now.strftime('%Y'))
            numero = numero.replace('{MM}', now.strftime('%m'))
            numero = numero.replace('{DD}', now.strftime('%d'))
            numero = numero.replace('{NUM}', str(numero_seq).zfill(4))
            
            cur.execute('UPDATE parametres_systeme SET prochain_numero_sequence = prochain_numero_sequence + 1')
            conn.commit()
            
            cur.close()
            conn.close()
            
            return jsonify({'numero': numero})
        
        cur.close()
        conn.close()
        return jsonify({'numero': f'RES-{datetime.now().strftime("%Y%m%d")}-0001'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sejours_bp.route('/api/sejours', methods=['POST'])
@login_required
def create_sejour():
    data = request.get_json()
    
    sejour_data = data.get('sejour', {}) or data.get('reservation', {})
    personnes_data = data.get('personnes', [])
    chambres_ids = data.get('chambres', [])
    
    sejour_id = Reservation.create(sejour_data)
    
    if sejour_id:
        if chambres_ids:
            conn = get_db_connection()
            cur = conn.cursor()
            for chambre_id in chambres_ids:
                cur.execute('''
                    INSERT INTO reservations_chambres (reservation_id, chambre_id)
                    VALUES (%s, %s)
                ''', (sejour_id, chambre_id))
            conn.commit()
            cur.close()
            conn.close()
        
        if personnes_data:
            for i, personne_data in enumerate(personnes_data):
                personne_data['reservation_id'] = sejour_id
                personne_data['est_contact_principal'] = (i == 0)
                Personne.create(personne_data)
    
    return jsonify({
        'success': True,
        'sejour_id': sejour_id,
        'message': 'Séjour créé avec succès'
    }), 201

@sejours_bp.route('/api/sejours/<int:sejour_id>', methods=['PUT'])
@login_required
def update_sejour(sejour_id):
    data = request.get_json()
    Reservation.update(sejour_id, data)
    return jsonify({'message': 'Séjour mis à jour avec succès'})

@sejours_bp.route('/api/sejours/<int:sejour_id>', methods=['DELETE'])
@login_required
def delete_sejour(sejour_id):
    Reservation.delete(sejour_id)
    return jsonify({'message': 'Séjour supprimé avec succès'})

@sejours_bp.route('/api/personnes', methods=['POST'])
@login_required
def add_personne():
    data = request.get_json()
    personne_id = Personne.create(data)
    return jsonify({
        'success': True,
        'personne_id': personne_id,
        'message': 'Personne ajoutée avec succès'
    }), 201

@sejours_bp.route('/api/personnes/<int:personne_id>', methods=['PUT'])
@login_required
def update_personne(personne_id):
    data = request.get_json()
    Personne.update(personne_id, data)
    return jsonify({'message': 'Personne mise à jour avec succès'})

@sejours_bp.route('/api/personnes/<int:personne_id>', methods=['DELETE'])
@login_required
def delete_personne(personne_id):
    Personne.delete(personne_id)
    return jsonify({'message': 'Personne supprimée avec succès'})

@sejours_bp.route('/api/personnes', methods=['GET'])
@login_required
def get_all_personnes():
    personnes = Personne.get_all()
    return jsonify(serialize_rows(personnes))

@sejours_bp.route('/api/sejours/<int:sejour_id>/close', methods=['POST'])
@login_required
def close_sejour(sejour_id):
    """Clôturer un séjour (empêche les modifications ultérieures)"""
    from flask_login import current_user
    from ..config.database import get_db_connection
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Vérifier que le séjour existe et n'est pas déjà clôturé
        cur.execute('SELECT statut, closed_at FROM reservations WHERE id = %s', (sejour_id,))
        sejour = cur.fetchone()
        
        if not sejour:
            return jsonify({'error': 'Séjour non trouvé'}), 404
        
        if sejour['statut'] == 'closed' or sejour['closed_at']:
            return jsonify({'error': 'Ce séjour est déjà clôturé'}), 400
        
        # Clôturer le séjour
        user_id = current_user.id if hasattr(current_user, 'id') else None
        cur.execute('''
            UPDATE reservations 
            SET statut = 'closed', closed_at = CURRENT_TIMESTAMP, closed_by = %s
            WHERE id = %s
        ''', (user_id, sejour_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Séjour clôturé avec succès'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
