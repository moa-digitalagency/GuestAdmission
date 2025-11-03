from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..models.reservation import Reservation
from ..models.personne import Personne
from ..utils import serialize_rows, serialize_row

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/api/reservations', methods=['GET'])
@login_required
def get_reservations():
    reservations = Reservation.get_all()
    return jsonify(serialize_rows(reservations))

@reservations_bp.route('/api/reservations/<int:reservation_id>', methods=['GET'])
@login_required
def get_reservation(reservation_id):
    reservation = Reservation.get_by_id(reservation_id)
    if reservation:
        personnes = Personne.get_by_reservation(reservation_id)
        return jsonify({
            'reservation': serialize_row(reservation),
            'personnes': serialize_rows(personnes)
        })
    return jsonify({'error': 'Réservation non trouvée'}), 404

@reservations_bp.route('/api/reservations', methods=['POST'])
@login_required
def create_reservation():
    data = request.get_json()
    
    reservation_data = data.get('reservation', {})
    personnes_data = data.get('personnes', [])
    
    reservation_id = Reservation.create(reservation_data)
    
    if reservation_id and personnes_data:
        for i, personne_data in enumerate(personnes_data):
            personne_data['reservation_id'] = reservation_id
            personne_data['est_contact_principal'] = (i == 0)
            Personne.create(personne_data)
    
    return jsonify({
        'success': True,
        'reservation_id': reservation_id,
        'message': 'Réservation créée avec succès'
    }), 201

@reservations_bp.route('/api/reservations/<int:reservation_id>', methods=['PUT'])
@login_required
def update_reservation(reservation_id):
    data = request.get_json()
    Reservation.update(reservation_id, data)
    return jsonify({'message': 'Réservation mise à jour avec succès'})

@reservations_bp.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
@login_required
def delete_reservation(reservation_id):
    Reservation.delete(reservation_id)
    return jsonify({'message': 'Réservation supprimée avec succès'})

@reservations_bp.route('/api/personnes', methods=['POST'])
@login_required
def add_personne():
    data = request.get_json()
    personne_id = Personne.create(data)
    return jsonify({
        'success': True,
        'personne_id': personne_id,
        'message': 'Personne ajoutée avec succès'
    }), 201

@reservations_bp.route('/api/personnes/<int:personne_id>', methods=['PUT'])
@login_required
def update_personne(personne_id):
    data = request.get_json()
    Personne.update(personne_id, data)
    return jsonify({'message': 'Personne mise à jour avec succès'})

@reservations_bp.route('/api/personnes/<int:personne_id>', methods=['DELETE'])
@login_required
def delete_personne(personne_id):
    Personne.delete(personne_id)
    return jsonify({'message': 'Personne supprimée avec succès'})

@reservations_bp.route('/api/personnes', methods=['GET'])
@login_required
def get_all_personnes():
    personnes = Personne.get_all()
    return jsonify(serialize_rows(personnes))
