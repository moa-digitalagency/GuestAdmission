from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models.user import User
from ..models.etablissement import Etablissement
from ..models.chambre import Chambre
from ..decorators.roles import super_admin_required
from ..utils.serializers import serialize_row, serialize_rows

super_admin_bp = Blueprint('super_admin', __name__)

@super_admin_bp.route('/api/super-admin/etablissements', methods=['POST'])
@login_required
@super_admin_required
def create_etablissement_with_admin():
    """Créer un établissement avec son administrateur principal"""
    data = request.get_json()
    
    etablissement_data = data.get('etablissement', {})
    admin_data = data.get('admin', {})
    
    if not etablissement_data.get('nom_etablissement'):
        return jsonify({'error': 'Nom de l\'établissement requis'}), 400
    
    if not admin_data.get('username') or not admin_data.get('password'):
        return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis pour l\'admin'}), 400
    
    try:
        etablissement_id = Etablissement.create(etablissement_data)
        
        if not etablissement_id:
            return jsonify({'error': 'Erreur lors de la création de l\'établissement'}), 500
        
        user_id = User.create(
            username=admin_data.get('username'),
            password=admin_data.get('password'),
            nom=admin_data.get('nom', ''),
            prenom=admin_data.get('prenom', ''),
            email=admin_data.get('email', ''),
            role='admin',
            etablissement_id=etablissement_id
        )
        
        if not user_id:
            return jsonify({'error': 'Erreur lors de la création de l\'administrateur'}), 500
        
        User.add_to_etablissement(user_id, etablissement_id, 'admin')
        
        return jsonify({
            'success': True,
            'message': 'Établissement et administrateur créés avec succès',
            'etablissement_id': etablissement_id,
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500

@super_admin_bp.route('/api/super-admin/etablissements', methods=['GET'])
@login_required
@super_admin_required
def get_all_etablissements():
    """Obtenir tous les établissements (super admin seulement)"""
    etablissements = Etablissement.get_all(actif_only=False)
    return jsonify(serialize_rows(etablissements))

@super_admin_bp.route('/api/super-admin/etablissements/<int:etablissement_id>/users', methods=['GET'])
@login_required
@super_admin_required
def get_etablissement_users(etablissement_id):
    """Obtenir tous les utilisateurs d'un établissement"""
    users = User.get_users_by_etablissement(etablissement_id)
    return jsonify(serialize_rows(users))

@super_admin_bp.route('/api/super-admin/etablissements/<int:etablissement_id>/users', methods=['POST'])
@login_required
@super_admin_required
def add_user_to_etablissement(etablissement_id):
    """Ajouter un utilisateur à un établissement"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
    
    try:
        user_id = User.create(
            username=data.get('username'),
            password=data.get('password'),
            nom=data.get('nom', ''),
            prenom=data.get('prenom', ''),
            email=data.get('email', ''),
            role='admin',
            etablissement_id=etablissement_id
        )
        
        if not user_id:
            return jsonify({'error': 'Erreur lors de la création de l\'utilisateur'}), 500
        
        User.add_to_etablissement(user_id, etablissement_id, 'admin')
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur créé et ajouté à l\'établissement',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}'}), 500

@super_admin_bp.route('/api/super-admin/etablissements/<int:etablissement_id>/users/<int:user_id>', methods=['DELETE'])
@login_required
@super_admin_required
def remove_user_from_etablissement(etablissement_id, user_id):
    """Retirer un utilisateur d'un établissement"""
    try:
        User.remove_from_etablissement(user_id, etablissement_id)
        return jsonify({'success': True, 'message': 'Utilisateur retiré de l\'établissement'})
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}'}), 500

@super_admin_bp.route('/api/super-admin/etablissements/<int:etablissement_id>/chambres', methods=['GET'])
@login_required
@super_admin_required
def get_etablissement_chambres(etablissement_id):
    """Obtenir toutes les chambres d'un établissement"""
    chambres = Chambre.get_by_etablissement(etablissement_id)
    return jsonify(serialize_rows(chambres))

@super_admin_bp.route('/api/super-admin/etablissements/<int:etablissement_id>/chambres', methods=['POST'])
@login_required
@super_admin_required
def create_chambre_for_etablissement(etablissement_id):
    """Créer une chambre pour un établissement"""
    data = request.get_json()
    data['etablissement_id'] = etablissement_id
    
    try:
        chambre_id = Chambre.create(data)
        return jsonify({
            'success': True,
            'message': 'Chambre créée avec succès',
            'chambre_id': chambre_id
        }), 201
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}'}), 500

@super_admin_bp.route('/api/super-admin/stats', methods=['GET'])
@login_required
@super_admin_required
def get_super_admin_stats():
    """Obtenir les statistiques globales pour le super admin"""
    from ..config.database import get_db_connection
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT COUNT(*) as count FROM etablissements WHERE actif = TRUE')
    etablissements_actifs = cur.fetchone()['count']
    
    cur.execute('SELECT COUNT(*) as count FROM etablissements')
    total_etablissements = cur.fetchone()['count']
    
    cur.execute('SELECT COUNT(*) as count FROM users WHERE role = \'admin\'')
    total_admins = cur.fetchone()['count']
    
    cur.execute('SELECT COUNT(*) as count FROM reservations')
    total_reservations = cur.fetchone()['count']
    
    cur.execute('SELECT COUNT(*) as count FROM chambres')
    total_chambres = cur.fetchone()['count']
    
    cur.close()
    conn.close()
    
    return jsonify({
        'etablissements_actifs': etablissements_actifs,
        'total_etablissements': total_etablissements,
        'total_admins': total_admins,
        'total_reservations': total_reservations,
        'total_chambres': total_chambres
    })
