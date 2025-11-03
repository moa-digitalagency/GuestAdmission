from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_page():
    if current_user.is_authenticated:
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
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'nom': current_user.nom,
        'prenom': current_user.prenom,
        'email': current_user.email,
        'role': current_user.role
    })
