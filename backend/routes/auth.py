from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
        if current_user.is_super_admin():
            return redirect(url_for('super_admin_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.verify_password(username, password)
    
    if user:
        login_user(user)
        return jsonify({'success': True, 'message': 'Connexion réussie'})
    
    return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/api/current-user')
@login_required
def current_user_info():
    etablissements = current_user.get_etablissements() if not current_user.is_super_admin() else []
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'nom': current_user.nom,
        'prenom': current_user.prenom,
        'email': current_user.email,
        'role': current_user.role,
        'etablissement_id': current_user.etablissement_id,
        'is_super_admin': current_user.is_super_admin(),
        'etablissements': [{'id': e['id'], 'nom_etablissement': e['nom_etablissement']} for e in etablissements]
    })

@auth_bp.route('/api/change-etablissement', methods=['POST'])
@login_required
def change_etablissement():
    """Changer l'établissement actuel de l'utilisateur"""
    data = request.get_json()
    etablissement_id = data.get('etablissement_id')
    
    if not etablissement_id:
        return jsonify({'error': 'ID établissement requis'}), 400
    
    if current_user.is_super_admin():
        return jsonify({'error': 'Super admin n\'a pas besoin de changer d\'établissement'}), 400
    
    if not current_user.has_access_to_etablissement(etablissement_id):
        return jsonify({'error': 'Vous n\'avez pas accès à cet établissement'}), 403
    
    User.update_current_etablissement(current_user.id, etablissement_id)
    current_user.etablissement_id = etablissement_id
    
    return jsonify({'success': True, 'message': 'Établissement changé avec succès'})
