"""
Routes pour la gestion des extras
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..services.extra_service import ExtraService

extras_bp = Blueprint('extras', __name__)


@extras_bp.route('/api/extras', methods=['GET'])
@login_required
def get_extras():
    """Récupérer tous les extras"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    actif_only = request.args.get('actif_only', 'true').lower() == 'true'
    
    extras = ExtraService.get_all_extras(etablissement_id, actif_only)
    return jsonify(extras)


@extras_bp.route('/api/extras/<int:extra_id>', methods=['GET'])
@login_required
def get_extra(extra_id):
    """Récupérer un extra par ID"""
    extra = ExtraService.get_extra_by_id(extra_id)
    if extra:
        return jsonify(extra)
    return jsonify({'error': 'Extra non trouvé'}), 404


@extras_bp.route('/api/extras', methods=['POST'])
@login_required
def create_extra():
    """Créer un nouvel extra"""
    data = request.get_json()
    extra_id = ExtraService.create_extra(data)
    
    if extra_id:
        return jsonify({
            'success': True,
            'extra_id': extra_id,
            'message': 'Extra créé avec succès'
        }), 201
    
    return jsonify({'error': 'Erreur lors de la création'}), 500


@extras_bp.route('/api/extras/<int:extra_id>', methods=['PUT'])
@login_required
def update_extra(extra_id):
    """Mettre à jour un extra"""
    data = request.get_json()
    ExtraService.update_extra(extra_id, data)
    return jsonify({'success': True, 'message': 'Extra mis à jour avec succès'})


@extras_bp.route('/api/extras/<int:extra_id>', methods=['DELETE'])
@login_required
def delete_extra(extra_id):
    """Supprimer un extra"""
    ExtraService.delete_extra(extra_id)
    return jsonify({'success': True, 'message': 'Extra supprimé avec succès'})


@extras_bp.route('/api/sejours/<int:sejour_id>/extras', methods=['GET'])
@login_required
def get_sejour_extras(sejour_id):
    """Récupérer les extras d'un séjour"""
    extras = ExtraService.get_extras_by_sejour(sejour_id)
    return jsonify(extras)


@extras_bp.route('/api/sejours/<int:sejour_id>/extras', methods=['POST'])
@login_required
def add_extra_to_sejour(sejour_id):
    """Ajouter un extra à un séjour"""
    data = request.get_json()
    extra_id = data.get('extra_id')
    quantite = data.get('quantite', 1)
    
    if not extra_id:
        return jsonify({'error': 'ID de l\'extra requis'}), 400
    
    sejour_extra_id = ExtraService.add_extra_to_sejour(sejour_id, extra_id, quantite)
    
    if sejour_extra_id:
        return jsonify({
            'success': True,
            'sejour_extra_id': sejour_extra_id,
            'message': 'Extra ajouté au séjour avec succès'
        }), 201
    
    return jsonify({'error': 'Erreur lors de l\'ajout'}), 500


@extras_bp.route('/api/sejours/extras/<int:sejour_extra_id>', methods=['DELETE'])
@login_required
def remove_extra_from_sejour(sejour_extra_id):
    """Retirer un extra d'un séjour"""
    ExtraService.remove_extra_from_sejour(sejour_extra_id)
    return jsonify({'success': True, 'message': 'Extra retiré du séjour'})


@extras_bp.route('/api/extras/summary/<int:etablissement_id>', methods=['GET'])
@login_required
def get_extras_summary(etablissement_id):
    """Récupérer le sommaire des extras par établissement"""
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    summary = ExtraService.get_extras_summary_by_etablissement(
        etablissement_id, date_debut, date_fin
    )
    return jsonify(summary)
