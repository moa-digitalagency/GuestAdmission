from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from ..config.database import get_db_connection
from werkzeug.utils import secure_filename
import json
import os
import time

parametres_bp = Blueprint('parametres', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@parametres_bp.route('/api/parametres', methods=['GET'])
@login_required
def get_parametres():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM parametres_systeme LIMIT 1')
    params = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if params:
        return jsonify(dict(params))
    return jsonify({})

@parametres_bp.route('/api/parametres/upload-logo', methods=['POST'])
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

@parametres_bp.route('/api/parametres', methods=['PUT'])
@login_required
def update_parametres():
    data = request.get_json()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    chambres_config = data.get('chambres_config', [])
    
    cur.execute('''
        UPDATE parametres_systeme
        SET nom_etablissement = %s,
            numero_identification = %s,
            pays = %s,
            ville = %s,
            adresse = %s,
            telephone = %s,
            whatsapp = %s,
            email = %s,
            devise = %s,
            taux_taxe_sejour = %s,
            taux_tva = %s,
            taux_charge_plateforme = %s,
            nombre_chambres = %s,
            prix_chambres = %s,
            responsables = %s,
            responsable_prenom = %s,
            responsable_nom = %s,
            responsable_email = %s,
            responsable_telephone = %s,
            logo_url = %s,
            format_numero_reservation = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (
        data.get('nom_etablissement'),
        data.get('numero_identification'),
        data.get('pays'),
        data.get('ville'),
        data.get('adresse'),
        data.get('telephone'),
        data.get('whatsapp'),
        data.get('email'),
        data.get('devise'),
        data.get('taux_taxe_sejour'),
        data.get('taux_tva'),
        data.get('taux_charge_plateforme'),
        data.get('nombre_chambres'),
        json.dumps(data.get('prix_chambres', [])),
        json.dumps(data.get('responsables', [])),
        data.get('responsable_prenom'),
        data.get('responsable_nom'),
        data.get('responsable_email'),
        data.get('responsable_telephone'),
        data.get('logo_url'),
        data.get('format_numero_reservation')
    ))
    
    cur.execute('DELETE FROM chambres')
    
    for chambre in chambres_config:
        cur.execute('''
            INSERT INTO chambres (nom, capacite, prix_par_nuit, statut)
            VALUES (%s, %s, %s, %s)
        ''', (
            chambre.get('nom'),
            chambre.get('capacite', 2),
            chambre.get('prix', 0),
            'disponible'
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Paramètres mis à jour avec succès'})
