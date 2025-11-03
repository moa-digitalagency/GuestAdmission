from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..config.database import get_db_connection
import json

parametres_bp = Blueprint('parametres', __name__)

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

@parametres_bp.route('/api/parametres', methods=['PUT'])
@login_required
def update_parametres():
    data = request.get_json()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        UPDATE parametres_systeme
        SET nom_etablissement = %s,
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
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (
        data.get('nom_etablissement'),
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
        data.get('responsable_telephone')
    ))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Paramètres mis à jour avec succès'})
