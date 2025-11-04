"""
Routes pour la gestion des calendriers iCal
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..services.calendar_service import CalendarService

calendars_bp = Blueprint('calendars', __name__)


@calendars_bp.route('/api/calendriers', methods=['GET'])
@login_required
def get_calendars():
    """Récupérer tous les calendriers"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    calendars = CalendarService.get_all_calendars(etablissement_id)
    return jsonify(calendars)


@calendars_bp.route('/api/calendriers/<int:calendar_id>', methods=['GET'])
@login_required
def get_calendar(calendar_id):
    """Récupérer un calendrier par son ID"""
    calendar = CalendarService.get_calendar_by_id(calendar_id)
    if calendar:
        return jsonify(calendar)
    return jsonify({'error': 'Calendrier non trouvé'}), 404


@calendars_bp.route('/api/calendriers', methods=['POST'])
@login_required
def create_calendar():
    """Créer un nouveau calendrier"""
    data = request.get_json()
    calendar_id = CalendarService.create_calendar(data)
    
    if calendar_id:
        return jsonify({
            'success': True,
            'calendar_id': calendar_id,
            'message': 'Calendrier créé avec succès'
        }), 201
    
    return jsonify({'error': 'Erreur lors de la création'}), 500


@calendars_bp.route('/api/calendriers/<int:calendar_id>', methods=['PUT'])
@login_required
def update_calendar(calendar_id):
    """Mettre à jour un calendrier"""
    data = request.get_json()
    success = CalendarService.update_calendar(calendar_id, data)
    
    if success:
        return jsonify({'success': True, 'message': 'Calendrier mis à jour'})
    
    return jsonify({'error': 'Erreur lors de la mise à jour'}), 500


@calendars_bp.route('/api/calendriers/<int:calendar_id>', methods=['DELETE'])
@login_required
def delete_calendar(calendar_id):
    """Supprimer un calendrier"""
    success = CalendarService.delete_calendar(calendar_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Calendrier supprimé'})
    
    return jsonify({'error': 'Erreur lors de la suppression'}), 500


@calendars_bp.route('/api/calendriers/<int:calendar_id>/synchroniser', methods=['POST'])
@login_required
def synchronize_calendar(calendar_id):
    """Synchroniser un calendrier avec sa source iCal"""
    result = CalendarService.synchronize_calendar(calendar_id)
    
    if result['success']:
        return jsonify(result)
    
    return jsonify(result), 400


@calendars_bp.route('/api/calendriers/<int:calendar_id>/reservations', methods=['GET'])
@login_required
def get_calendar_reservations(calendar_id):
    """Récupérer les réservations d'un calendrier"""
    reservations = CalendarService.get_calendar_reservations(calendar_id)
    return jsonify(reservations)


@calendars_bp.route('/api/reservations-ical', methods=['GET'])
@login_required
def get_all_ical_reservations():
    """Récupérer toutes les réservations iCal avec filtres"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    reservations = CalendarService.get_all_ical_reservations(
        etablissement_id, date_debut, date_fin
    )
    return jsonify(reservations)
