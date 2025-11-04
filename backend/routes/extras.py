"""
Routes pour la gestion des extras
"""
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required
from ..services.extra_service import ExtraService
from ..services.invoice_service import InvoiceService

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
    # Vérifier que le séjour n'est pas clôturé
    if ExtraService.is_sejour_closed(sejour_id):
        return jsonify({'error': 'Ce séjour est clôturé, impossible d\'ajouter des extras'}), 403
    
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


@extras_bp.route('/api/sejours/extras/<int:sejour_extra_id>', methods=['PUT'])
@login_required
def update_sejour_extra(sejour_extra_id):
    """Mettre à jour la quantité d'un extra dans un séjour"""
    # Vérifier que le séjour n'est pas clôturé
    sejour_id = ExtraService.get_sejour_id_from_extra(sejour_extra_id)
    if sejour_id and ExtraService.is_sejour_closed(sejour_id):
        return jsonify({'error': 'Ce séjour est clôturé, impossible de modifier les extras'}), 403
    
    data = request.get_json()
    quantite = data.get('quantite', 1)
    
    ExtraService.update_sejour_extra(sejour_extra_id, quantite)
    return jsonify({'success': True, 'message': 'Extra mis à jour avec succès'})


@extras_bp.route('/api/sejours/extras/<int:sejour_extra_id>', methods=['DELETE'])
@login_required
def remove_extra_from_sejour(sejour_extra_id):
    """Retirer un extra d'un séjour"""
    # Vérifier que le séjour n'est pas clôturé
    sejour_id = ExtraService.get_sejour_id_from_extra(sejour_extra_id)
    if sejour_id and ExtraService.is_sejour_closed(sejour_id):
        return jsonify({'error': 'Ce séjour est clôturé, impossible de supprimer les extras'}), 403
    
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


@extras_bp.route('/api/sejours/<int:sejour_id>/facture', methods=['POST'])
@login_required
def generate_invoice(sejour_id):
    """Générer une facture PDF pour un séjour"""
    try:
        pdf_buffer = InvoiceService.generate_sejour_invoice(sejour_id)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'facture_sejour_{sejour_id}.pdf'
        )
    except ValueError as e:
        error_msg = str(e)
        # Distinguer entre séjour non trouvé et séjour non clôturé
        if 'non trouvé' in error_msg or 'not found' in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        else:
            # Séjour existe mais pas clôturé = violation de règle métier
            return jsonify({'error': error_msg}), 403
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération de la facture: {str(e)}'}), 500
