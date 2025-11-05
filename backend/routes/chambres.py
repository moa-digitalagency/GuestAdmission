from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..utils.tenant_context import (
    get_accessible_etablissement_ids,
    verify_etablissement_access
)
from ..config.database import get_db_connection

chambres_bp = Blueprint('chambres', __name__)

@chambres_bp.route('/api/chambres', methods=['GET'])
@login_required
def get_chambres():
    """Récupérer les chambres accessibles"""
    try:
        etablissement_id = request.args.get('etablissement_id', type=int)
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Filtrer par établissements accessibles
        etablissement_ids = get_accessible_etablissement_ids()
        
        if etablissement_id:
            # Vérifier l'accès à l'établissement demandé
            if not verify_etablissement_access(etablissement_id):
                return jsonify({'error': 'Accès refusé à cet établissement'}), 403
            
            cur.execute('''
                SELECT id, etablissement_id, nom, description, capacite, prix_par_nuit, statut, created_at
                FROM chambres
                WHERE etablissement_id = %s
                ORDER BY nom
            ''', (etablissement_id,))
        elif etablissement_ids is None:  # PLATFORM_ADMIN
            cur.execute('''
                SELECT id, etablissement_id, nom, description, capacite, prix_par_nuit, statut, created_at
                FROM chambres
                ORDER BY nom
            ''')
        elif etablissement_ids:
            placeholders = ','.join(['%s'] * len(etablissement_ids))
            cur.execute(f'''
                SELECT id, etablissement_id, nom, description, capacite, prix_par_nuit, statut, created_at
                FROM chambres
                WHERE etablissement_id IN ({placeholders})
                ORDER BY nom
            ''', tuple(etablissement_ids))
        else:
            return jsonify([])
        
        chambres = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([dict(c) for c in chambres])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres', methods=['POST'])
@login_required
def create_chambre():
    """Créer une nouvelle chambre"""
    try:
        data = request.get_json()
        etablissement_id = data.get('etablissement_id')
        
        if not etablissement_id:
            return jsonify({'error': 'etablissement_id requis'}), 400
        
        # Vérifier l'accès à l'établissement
        if not verify_etablissement_access(etablissement_id):
            return jsonify({'error': 'Accès refusé à cet établissement'}), 403
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, etablissement_id, nom, description, capacite, prix_par_nuit, statut
        ''', (
            etablissement_id,
            data.get('nom'),
            data.get('description', ''),
            data.get('capacite', 2),
            data.get('prix_par_nuit', 0),
            data.get('statut', 'disponible')
        ))
        
        chambre = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify(dict(chambre)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres/<int:chambre_id>', methods=['GET'])
@login_required
def get_chambre(chambre_id):
    """Récupérer une chambre spécifique"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id, etablissement_id, nom, description, capacite, prix_par_nuit, statut, created_at
            FROM chambres
            WHERE id = %s
        ''', (chambre_id,))
        
        chambre = cur.fetchone()
        cur.close()
        conn.close()
        
        if not chambre:
            return jsonify({'error': 'Chambre non trouvée'}), 404
        
        # Vérifier l'accès à l'établissement
        if not verify_etablissement_access(chambre['etablissement_id']):
            return jsonify({'error': 'Accès refusé'}), 403
        
        return jsonify(dict(chambre))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres/<int:chambre_id>', methods=['PUT'])
@login_required
def update_chambre(chambre_id):
    """Mettre à jour une chambre"""
    try:
        # Vérifier l'accès à la chambre
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT etablissement_id FROM chambres WHERE id = %s', (chambre_id,))
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            return jsonify({'error': 'Chambre non trouvée'}), 404
        
        if not verify_etablissement_access(result['etablissement_id']):
            cur.close()
            conn.close()
            return jsonify({'error': 'Accès refusé'}), 403
        
        data = request.get_json()
        
        cur.execute('''
            UPDATE chambres
            SET nom = %s, description = %s, capacite = %s, prix_par_nuit = %s, statut = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, nom, description, capacite, prix_par_nuit, statut
        ''', (
            data.get('nom'),
            data.get('description'),
            data.get('capacite'),
            data.get('prix_par_nuit'),
            data.get('statut'),
            chambre_id
        ))
        
        chambre = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if chambre:
            return jsonify(dict(chambre))
        return jsonify({'error': 'Chambre non trouvée'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres/<int:chambre_id>', methods=['DELETE'])
@login_required
def delete_chambre(chambre_id):
    """Supprimer une chambre"""
    try:
        # Vérifier l'accès à la chambre
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT etablissement_id FROM chambres WHERE id = %s', (chambre_id,))
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            return jsonify({'error': 'Chambre non trouvée'}), 404
        
        if not verify_etablissement_access(result['etablissement_id']):
            cur.close()
            conn.close()
            return jsonify({'error': 'Accès refusé'}), 403
        
        cur.execute('DELETE FROM chambres WHERE id = %s RETURNING id', (chambre_id,))
        deleted = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        if deleted:
            return jsonify({'message': 'Chambre supprimée'})
        return jsonify({'error': 'Chambre non trouvée'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chambres_bp.route('/api/chambres/disponibles', methods=['GET'])
@login_required
def get_chambres_disponibles():
    """Récupérer les chambres disponibles"""
    try:
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        etablissement_id = request.args.get('etablissement_id', type=int)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Filtrer par établissements accessibles
        etablissement_ids = get_accessible_etablissement_ids()
        
        if etablissement_id:
            if not verify_etablissement_access(etablissement_id):
                return jsonify({'error': 'Accès refusé à cet établissement'}), 403
            where_clause = 'AND c.etablissement_id = %s'
            params_etablissement = [etablissement_id]
        elif etablissement_ids is None:  # PLATFORM_ADMIN
            where_clause = ''
            params_etablissement = []
        elif etablissement_ids:
            placeholders = ','.join(['%s'] * len(etablissement_ids))
            where_clause = f'AND c.etablissement_id IN ({placeholders})'
            params_etablissement = list(etablissement_ids)
        else:
            return jsonify([])
        
        if date_debut and date_fin:
            query = f'''
                SELECT c.id, c.nom, c.description, c.capacite, c.prix_par_nuit
                FROM chambres c
                WHERE c.statut = 'disponible'
                {where_clause}
                AND c.id NOT IN (
                    SELECT DISTINCT rc.chambre_id
                    FROM reservations_chambres rc
                    JOIN reservations r ON rc.reservation_id = r.id
                    WHERE r.statut != 'annulée'
                    AND (
                        (r.date_arrivee <= %s AND r.date_depart >= %s)
                        OR (r.date_arrivee <= %s AND r.date_depart >= %s)
                        OR (r.date_arrivee >= %s AND r.date_depart <= %s)
                    )
                )
                ORDER BY c.nom
            '''
            params = params_etablissement + [date_fin, date_debut, date_fin, date_fin, date_debut, date_fin]
            cur.execute(query, params)
        else:
            query = f'''
                SELECT id, nom, description, capacite, prix_par_nuit
                FROM chambres
                WHERE statut = 'disponible'
                {where_clause}
                ORDER BY nom
            '''
            cur.execute(query, params_etablissement)
        
        chambres = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify([dict(c) for c in chambres])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
