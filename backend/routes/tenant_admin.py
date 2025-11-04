from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models.user import User
from ..models.etablissement import Etablissement
from ..models.chambre import Chambre
from ..decorators.roles import tenant_admin_required
from ..utils.serializers import serialize_row, serialize_rows
from ..config.database import get_db_connection

tenant_admin_bp = Blueprint('tenant_admin', __name__)

# ============== GESTION DES ÉTABLISSEMENTS (TENANT) ==============

@tenant_admin_bp.route('/api/tenant/etablissements', methods=['GET'])
@login_required
@tenant_admin_required
def get_my_etablissements():
    """Obtenir les établissements du compte tenant de l'admin connecté"""
    etablissements = current_user.get_etablissements()
    return jsonify(serialize_rows(etablissements))

@tenant_admin_bp.route('/api/tenant/etablissements', methods=['POST'])
@login_required
@tenant_admin_required
def create_etablissement():
    """
    Créer un nouvel établissement pour le compte tenant de l'admin
    L'admin peut ajouter des établissements supplémentaires à son compte
    """
    data = request.get_json()
    
    if not data.get('nom_etablissement'):
        return jsonify({'error': 'Nom de l\'établissement requis'}), 400
    
    try:
        # Récupérer le tenant_account_id de l'utilisateur
        tenant_account_id = current_user.get_tenant_account_id()
        
        if not tenant_account_id:
            return jsonify({'error': 'Aucun compte tenant associé à cet utilisateur'}), 400
        
        # Créer l'établissement
        etablissement_id = Etablissement.create(data)
        
        if not etablissement_id:
            return jsonify({'error': 'Erreur lors de la création de l\'établissement'}), 500
        
        # Associer l'établissement au même tenant_account_id
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE etablissements 
            SET tenant_account_id = %s 
            WHERE id = %s
        ''', (tenant_account_id, etablissement_id))
        conn.commit()
        
        # Ajouter l'utilisateur courant à cet établissement
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, etablissement_id) DO NOTHING
        ''', (current_user.id, etablissement_id, 'admin'))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Établissement créé avec succès',
            'etablissement_id': etablissement_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500

@tenant_admin_bp.route('/api/tenant/etablissements/<int:etablissement_id>', methods=['PUT'])
@login_required
@tenant_admin_required
def update_etablissement(etablissement_id):
    """Mettre à jour un établissement (seulement si l'admin y a accès)"""
    if not current_user.can_manage_etablissement(etablissement_id):
        return jsonify({'error': 'Accès refusé à cet établissement'}), 403
    
    data = request.get_json()
    Etablissement.update(etablissement_id, data)
    return jsonify({'success': True, 'message': 'Établissement mis à jour avec succès'})

@tenant_admin_bp.route('/api/tenant/etablissements/<int:etablissement_id>', methods=['DELETE'])
@login_required
@tenant_admin_required
def delete_etablissement(etablissement_id):
    """Supprimer un établissement (seulement si l'admin y a accès)"""
    if not current_user.can_manage_etablissement(etablissement_id):
        return jsonify({'error': 'Accès refusé à cet établissement'}), 403
    
    Etablissement.delete(etablissement_id)
    return jsonify({'success': True, 'message': 'Établissement supprimé avec succès'})

# ============== GESTION DES CHAMBRES (TENANT) ==============

@tenant_admin_bp.route('/api/tenant/etablissements/<int:etablissement_id>/chambres', methods=['GET'])
@login_required
@tenant_admin_required
def get_etablissement_chambres(etablissement_id):
    """Obtenir toutes les chambres d'un établissement"""
    if not current_user.can_manage_etablissement(etablissement_id):
        return jsonify({'error': 'Accès refusé à cet établissement'}), 403
    
    chambres = Chambre.get_by_etablissement(etablissement_id)
    return jsonify(serialize_rows(chambres))

@tenant_admin_bp.route('/api/tenant/etablissements/<int:etablissement_id>/chambres', methods=['POST'])
@login_required
@tenant_admin_required
def create_chambre(etablissement_id):
    """Créer une chambre pour un établissement"""
    if not current_user.can_manage_etablissement(etablissement_id):
        return jsonify({'error': 'Accès refusé à cet établissement'}), 403
    
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

# ============== GESTION DES UTILISATEURS (TENANT) ==============

@tenant_admin_bp.route('/api/tenant/users', methods=['GET'])
@login_required
@tenant_admin_required
def get_my_users():
    """Obtenir tous les utilisateurs ayant accès aux établissements du tenant"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Récupérer le tenant_account_id
    tenant_account_id = current_user.get_tenant_account_id()
    
    if not tenant_account_id:
        return jsonify([])
    
    # Obtenir tous les utilisateurs des établissements de ce tenant
    cur.execute('''
        SELECT DISTINCT u.*, 
               STRING_AGG(DISTINCT e.nom_etablissement, ', ') as etablissements
        FROM users u
        INNER JOIN user_etablissements ue ON u.id = ue.user_id
        INNER JOIN etablissements e ON ue.etablissement_id = e.id
        WHERE e.tenant_account_id = %s
        GROUP BY u.id
        ORDER BY u.nom, u.prenom
    ''', (tenant_account_id,))
    
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([dict(u) for u in users] if users else [])

@tenant_admin_bp.route('/api/tenant/users', methods=['POST'])
@login_required
@tenant_admin_required
def add_user():
    """
    Ajouter un nouvel utilisateur au compte tenant
    L'utilisateur aura accès aux établissements spécifiés
    """
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
    
    etablissement_ids = data.get('etablissement_ids', [])
    
    if not etablissement_ids:
        return jsonify({'error': 'Au moins un établissement doit être sélectionné'}), 400
    
    # Vérifier que l'admin a accès à tous les établissements spécifiés
    for etab_id in etablissement_ids:
        if not current_user.can_manage_etablissement(etab_id):
            return jsonify({'error': f'Accès refusé à l\'établissement {etab_id}'}), 403
    
    try:
        # Créer l'utilisateur
        user_id = User.create(
            username=data.get('username'),
            password=data.get('password'),
            nom=data.get('nom', ''),
            prenom=data.get('prenom', ''),
            email=data.get('email', ''),
            role='admin',  # Par défaut, les utilisateurs ajoutés sont des admins
            etablissement_id=etablissement_ids[0] if etablissement_ids else None
        )
        
        if not user_id:
            return jsonify({'error': 'Erreur lors de la création de l\'utilisateur'}), 500
        
        # Ajouter l'utilisateur à tous les établissements spécifiés
        for etab_id in etablissement_ids:
            User.add_to_etablissement(user_id, etab_id, 'admin')
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur créé et ajouté aux établissements',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}'}), 500

@tenant_admin_bp.route('/api/tenant/users/<int:user_id>', methods=['DELETE'])
@login_required
@tenant_admin_required
def remove_user(user_id):
    """Retirer un utilisateur du compte tenant"""
    # Vérifier que l'utilisateur à supprimer appartient au même tenant
    conn = get_db_connection()
    cur = conn.cursor()
    
    tenant_account_id = current_user.get_tenant_account_id()
    
    if not tenant_account_id:
        return jsonify({'error': 'Aucun compte tenant associé'}), 400
    
    # Vérifier que l'utilisateur à supprimer appartient au tenant
    cur.execute('''
        SELECT COUNT(*) as count
        FROM user_etablissements ue
        INNER JOIN etablissements e ON ue.etablissement_id = e.id
        WHERE ue.user_id = %s AND e.tenant_account_id = %s
    ''', (user_id, tenant_account_id))
    
    result = cur.fetchone()
    
    if not result or result['count'] == 0:
        cur.close()
        conn.close()
        return jsonify({'error': 'Utilisateur non trouvé dans ce compte tenant'}), 404
    
    # Supprimer l'utilisateur
    cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Utilisateur supprimé avec succès'})

@tenant_admin_bp.route('/api/tenant/users/<int:user_id>/etablissements', methods=['PUT'])
@login_required
@tenant_admin_required
def update_user_etablissements(user_id):
    """Mettre à jour les établissements auxquels un utilisateur a accès"""
    data = request.get_json()
    etablissement_ids = data.get('etablissement_ids', [])
    
    # Vérifier que l'admin a accès à tous les établissements spécifiés
    for etab_id in etablissement_ids:
        if not current_user.can_manage_etablissement(etab_id):
            return jsonify({'error': f'Accès refusé à l\'établissement {etab_id}'}), 403
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Supprimer les anciennes associations
        tenant_account_id = current_user.get_tenant_account_id()
        cur.execute('''
            DELETE FROM user_etablissements
            WHERE user_id = %s 
            AND etablissement_id IN (
                SELECT id FROM etablissements WHERE tenant_account_id = %s
            )
        ''', (user_id, tenant_account_id))
        
        # Ajouter les nouvelles associations
        for etab_id in etablissement_ids:
            cur.execute('''
                INSERT INTO user_etablissements (user_id, etablissement_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, etablissement_id) DO NOTHING
            ''', (user_id, etab_id, 'admin'))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Établissements de l\'utilisateur mis à jour'})
        
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}'}), 500

# ============== STATISTIQUES TENANT ==============

@tenant_admin_bp.route('/api/tenant/stats', methods=['GET'])
@login_required
@tenant_admin_required
def get_tenant_stats():
    """Obtenir les statistiques du compte tenant de l'admin"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    tenant_account_id = current_user.get_tenant_account_id()
    
    if not tenant_account_id:
        return jsonify({})
    
    # Nombre d'établissements
    cur.execute('''
        SELECT COUNT(*) as count FROM etablissements 
        WHERE tenant_account_id = %s
    ''', (tenant_account_id,))
    nb_etablissements = cur.fetchone()['count']
    
    # Nombre de chambres
    cur.execute('''
        SELECT COUNT(*) as count FROM chambres c
        INNER JOIN etablissements e ON c.etablissement_id = e.id
        WHERE e.tenant_account_id = %s
    ''', (tenant_account_id,))
    nb_chambres = cur.fetchone()['count']
    
    # Nombre de réservations
    cur.execute('''
        SELECT COUNT(*) as count FROM reservations r
        INNER JOIN etablissements e ON r.etablissement_id = e.id
        WHERE e.tenant_account_id = %s
    ''', (tenant_account_id,))
    nb_reservations = cur.fetchone()['count']
    
    # Nombre d'utilisateurs
    cur.execute('''
        SELECT COUNT(DISTINCT ue.user_id) as count
        FROM user_etablissements ue
        INNER JOIN etablissements e ON ue.etablissement_id = e.id
        WHERE e.tenant_account_id = %s
    ''', (tenant_account_id,))
    nb_users = cur.fetchone()['count']
    
    cur.close()
    conn.close()
    
    return jsonify({
        'nb_etablissements': nb_etablissements,
        'nb_chambres': nb_chambres,
        'nb_reservations': nb_reservations,
        'nb_users': nb_users
    })
