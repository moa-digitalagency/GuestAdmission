from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from ..models.etablissement import Etablissement
from ..utils import serialize_rows, serialize_row
from werkzeug.utils import secure_filename
import os
import time

etablissements_bp = Blueprint('etablissements', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@etablissements_bp.route('/api/etablissements', methods=['GET'])
@login_required
def get_etablissements():
    actif_only = request.args.get('actif_only', 'true').lower() == 'true'
    etablissements = current_user.get_etablissements(actif_only=actif_only)
    return jsonify(serialize_rows(etablissements))

@etablissements_bp.route('/api/etablissements/<int:etablissement_id>', methods=['GET'])
@login_required
def get_etablissement(etablissement_id):
    etablissement = Etablissement.get_by_id(etablissement_id)
    if etablissement:
        return jsonify(serialize_row(etablissement))
    return jsonify({'error': 'Établissement non trouvé'}), 404

@etablissements_bp.route('/api/etablissements', methods=['POST'])
@login_required
def create_etablissement():
    data = request.get_json()
    etablissement_id = Etablissement.create(data)
    return jsonify({
        'success': True,
        'etablissement_id': etablissement_id,
        'message': 'Établissement créé avec succès'
    }), 201

@etablissements_bp.route('/api/etablissements/<int:etablissement_id>', methods=['PUT'])
@login_required
def update_etablissement(etablissement_id):
    data = request.get_json()
    Etablissement.update(etablissement_id, data)
    return jsonify({'success': True, 'message': 'Établissement mis à jour avec succès'})

@etablissements_bp.route('/api/etablissements/<int:etablissement_id>', methods=['DELETE'])
@login_required
def delete_etablissement(etablissement_id):
    Etablissement.delete(etablissement_id)
    return jsonify({'success': True, 'message': 'Établissement supprimé avec succès'})

@etablissements_bp.route('/api/etablissements/<int:etablissement_id>/generer-numero', methods=['GET'])
@login_required
def generer_numero_reservation(etablissement_id):
    numero = Etablissement.generer_numero_reservation(etablissement_id)
    if numero:
        return jsonify({'numero': numero})
    return jsonify({'error': 'Impossible de générer le numéro'}), 400

@etablissements_bp.route('/api/etablissements/upload-logo', methods=['POST'])
@login_required
def upload_logo():
    if 'logo' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['logo']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if file and allowed_file(file.filename):
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time() * 1000))
        filename = f"logo_{timestamp}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logo_url = f"/static/uploads/{filename}"
        return jsonify({'success': True, 'logo_url': logo_url})
    
    return jsonify({'error': 'Type de fichier non autorisé'}), 400
