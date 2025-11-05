from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models.user import User
from ..models.etablissement import Etablissement
from ..models.chambre import Chambre
from ..models.tenant_account import TenantAccount
from ..decorators.roles import platform_admin_required
from ..utils.serializers import serialize_row, serialize_rows
from ..config.database import get_db_connection

platform_admin_bp = Blueprint('platform_admin', __name__)

# ============== GESTION DES COMPTES TENANTS ==============

@platform_admin_bp.route('/api/platform-admin/tenants', methods=['GET'])
@login_required
@platform_admin_required
def get_all_tenants():
    """Obtenir tous les comptes tenants"""
    actif_only = request.args.get('actif_only', 'true').lower() == 'true'
    tenants = TenantAccount.get_all(actif_only=actif_only)
    
    # Enrichir avec les statistiques
    result = []
    for tenant in tenants:
        tenant_dict = dict(tenant)
        stats = TenantAccount.get_stats(tenant['id'])
        tenant_dict.update(stats)
        result.append(tenant_dict)
    
    return jsonify(result)

@platform_admin_bp.route('/api/platform-admin/tenants/<int:tenant_id>', methods=['GET'])
@login_required
@platform_admin_required
def get_tenant(tenant_id):
    """Obtenir un compte tenant spécifique"""
    tenant = TenantAccount.get_by_id(tenant_id)
    if tenant:
        tenant_dict = dict(tenant)
        stats = TenantAccount.get_stats(tenant_id)
        tenant_dict.update(stats)
        return jsonify(tenant_dict)
    return jsonify({'error': 'Compte tenant non trouvé'}), 404

@platform_admin_bp.route('/api/platform-admin/tenants', methods=['POST'])
@login_required
@platform_admin_required
def create_tenant_with_etablissement():
    """
    Créer un nouveau compte tenant avec son premier établissement et admin principal
    """
    data = request.get_json()
    
    tenant_data = data.get('tenant', {})
    etablissement_data = data.get('etablissement', {})
    admin_data = data.get('admin', {})
    
    # Validation
    if not tenant_data.get('nom_compte'):
        return jsonify({'error': 'Nom du compte tenant requis'}), 400
    
    if not etablissement_data.get('nom_etablissement'):
        return jsonify({'error': 'Nom de l\'établissement requis'}), 400
    
    if not admin_data.get('username') or not admin_data.get('password'):
        return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis pour l\'admin'}), 400
    
    try:
        # 1. Créer l'utilisateur admin principal d'abord
        user_id = User.create(
            username=admin_data.get('username'),
            password=admin_data.get('password'),
            nom=admin_data.get('nom', ''),
            prenom=admin_data.get('prenom', ''),
            email=admin_data.get('email', ''),
            role='admin',
            etablissement_id=None  # Sera défini après la création de l'établissement
        )
        
        if not user_id:
            return jsonify({'error': 'Erreur lors de la création de l\'administrateur'}), 500
        
        # 2. Créer le compte tenant
        tenant_id = TenantAccount.create(
            nom_compte=tenant_data.get('nom_compte'),
            primary_admin_user_id=user_id,
            notes=tenant_data.get('notes', '')
        )
        
        if not tenant_id:
            return jsonify({'error': 'Erreur lors de la création du compte tenant'}), 500
        
        # 3. Créer l'établissement et l'associer au tenant
        etablissement_id = Etablissement.create(etablissement_data)
        
        if not etablissement_id:
            return jsonify({'error': 'Erreur lors de la création de l\'établissement'}), 500
        
        # 4. Associer l'établissement au tenant
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE etablissements 
            SET tenant_account_id = %s 
            WHERE id = %s
        ''', (tenant_id, etablissement_id))
        conn.commit()
        cur.close()
        conn.close()
        
        # 5. Mettre à jour l'etablissement_id de l'utilisateur
        User.update_current_etablissement(user_id, etablissement_id)
        
        # 6. Ajouter l'utilisateur à l'établissement avec le flag primary_admin
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role, is_primary_admin)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, etablissement_id) DO UPDATE SET is_primary_admin = TRUE
        ''', (user_id, etablissement_id, 'admin', True))
        conn.commit()
        cur.close()
        conn.close()
        
        # 7. Créer les chambres initiales si fournies
        chambres_data = data.get('chambres', [])
        chambres_created = []
        for chambre_data in chambres_data:
            chambre_id = Chambre.create({
                'etablissement_id': etablissement_id,
                'nom': chambre_data.get('nom'),
                'capacite': chambre_data.get('capacite', 2),
                'prix_par_nuit': chambre_data.get('prix_par_nuit', 0),
                'description': chambre_data.get('description', ''),
                'statut': 'disponible'
            })
            if chambre_id:
                chambres_created.append(chambre_id)
        
        return jsonify({
            'success': True,
            'message': 'Compte tenant, établissement et administrateur créés avec succès',
            'tenant_id': tenant_id,
            'etablissement_id': etablissement_id,
            'user_id': user_id,
            'chambres_created': len(chambres_created)
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500

@platform_admin_bp.route('/api/platform-admin/tenants/<int:tenant_id>', methods=['PUT'])
@login_required
@platform_admin_required
def update_tenant(tenant_id):
    """Mettre à jour un compte tenant"""
    data = request.get_json()
    TenantAccount.update(tenant_id, data)
    return jsonify({'success': True, 'message': 'Compte tenant mis à jour avec succès'})

@platform_admin_bp.route('/api/platform-admin/tenants/<int:tenant_id>', methods=['DELETE'])
@login_required
@platform_admin_required
def delete_tenant(tenant_id):
    """Désactiver un compte tenant (soft delete)"""
    TenantAccount.delete(tenant_id)
    return jsonify({'success': True, 'message': 'Compte tenant désactivé avec succès'})

# ============== GESTION DES ÉTABLISSEMENTS ==============

@platform_admin_bp.route('/api/platform-admin/etablissements', methods=['GET'])
@login_required
@platform_admin_required
def get_all_etablissements():
    """Obtenir tous les établissements (tous tenants)"""
    etablissements = Etablissement.get_all(actif_only=False)
    return jsonify(serialize_rows(etablissements))

@platform_admin_bp.route('/api/platform-admin/tenants/<int:tenant_id>/etablissements', methods=['GET'])
@login_required
@platform_admin_required
def get_tenant_etablissements(tenant_id):
    """Obtenir tous les établissements d'un tenant spécifique"""
    etablissements = TenantAccount.get_etablissements(tenant_id)
    return jsonify(serialize_rows(etablissements))

@platform_admin_bp.route('/api/platform-admin/etablissements/<int:etablissement_id>/users', methods=['GET'])
@login_required
@platform_admin_required
def get_etablissement_users(etablissement_id):
    """Obtenir tous les utilisateurs d'un établissement"""
    users = User.get_users_by_etablissement(etablissement_id)
    return jsonify(serialize_rows(users))

# ============== STATISTIQUES GLOBALES ==============

@platform_admin_bp.route('/api/platform-admin/stats', methods=['GET'])
@login_required
@platform_admin_required
def get_platform_stats():
    """Obtenir les statistiques globales de la plateforme"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Nombre de comptes tenants actifs
    cur.execute('SELECT COUNT(*) as count FROM tenant_accounts WHERE actif = TRUE')
    tenants_actifs = cur.fetchone()['count']
    
    # Nombre total de tenants
    cur.execute('SELECT COUNT(*) as count FROM tenant_accounts')
    total_tenants = cur.fetchone()['count']
    
    # Nombre d'établissements actifs
    cur.execute('SELECT COUNT(*) as count FROM etablissements WHERE actif = TRUE')
    etablissements_actifs = cur.fetchone()['count']
    
    # Nombre total d'établissements
    cur.execute('SELECT COUNT(*) as count FROM etablissements')
    total_etablissements = cur.fetchone()['count']
    
    # Nombre d'admins (tenant admins)
    cur.execute('SELECT COUNT(*) as count FROM users WHERE role = \'admin\'')
    total_admins = cur.fetchone()['count']
    
    # Nombre total de séjours
    cur.execute('SELECT COUNT(*) as count FROM reservations')
    total_sejours = cur.fetchone()['count']
    
    # Nombre total de chambres
    cur.execute('SELECT COUNT(*) as count FROM chambres')
    total_chambres = cur.fetchone()['count']
    
    # Séjours par tenant (top 5)
    cur.execute('''
        SELECT ta.nom_compte, COUNT(r.id) as nb_sejours
        FROM tenant_accounts ta
        LEFT JOIN etablissements e ON e.tenant_account_id = ta.id
        LEFT JOIN reservations r ON r.etablissement_id = e.id
        WHERE ta.actif = TRUE
        GROUP BY ta.id, ta.nom_compte
        ORDER BY nb_sejours DESC
        LIMIT 5
    ''')
    top_tenants = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify({
        'tenants_actifs': tenants_actifs,
        'total_tenants': total_tenants,
        'etablissements_actifs': etablissements_actifs,
        'total_etablissements': total_etablissements,
        'total_admins': total_admins,
        'total_sejours': total_sejours,
        'total_chambres': total_chambres,
        'top_tenants': [dict(t) for t in top_tenants] if top_tenants else []
    })

# ============== GESTION DES UTILISATEURS ==============

@platform_admin_bp.route('/api/platform-admin/users', methods=['GET'])
@login_required
@platform_admin_required
def get_all_users():
    """Obtenir tous les utilisateurs de la plateforme"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT u.*, COUNT(DISTINCT ue.etablissement_id) as nb_etablissements
        FROM users u
        LEFT JOIN user_etablissements ue ON u.id = ue.user_id
        WHERE u.role != 'PLATFORM_ADMIN'
        GROUP BY u.id
        ORDER BY u.nom, u.prenom
    ''')
    
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([dict(u) for u in users] if users else [])

@platform_admin_bp.route('/api/platform-admin/users/<int:user_id>', methods=['DELETE'])
@login_required
@platform_admin_required
def delete_user(user_id):
    """Supprimer un utilisateur"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('DELETE FROM users WHERE id = %s AND role != \'PLATFORM_ADMIN\'', (user_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Utilisateur supprimé avec succès'})
