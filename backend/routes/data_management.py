"""
Routes pour la gestion des données (démonstration, réinitialisation)
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
import subprocess
import os

data_bp = Blueprint('data', __name__)

def admin_required(f):
    """Décorateur pour restreindre l'accès aux administrateurs uniquement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'Authentification requise'}), 401
        
        user_role = getattr(current_user, 'role', None)
        if user_role != 'admin':
            return jsonify({'success': False, 'error': 'Accès réservé aux administrateurs'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@data_bp.route('/api/load-demo-data', methods=['POST'])
@login_required
@admin_required
def load_demo_data():
    """Charger les données de démonstration"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'load_demo_data.py')
        result = subprocess.run(
            ['python3', script_path, '--force'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Données de démonstration chargées avec succès'})
        else:
            return jsonify({'success': False, 'error': result.stderr or 'Erreur lors du chargement'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@data_bp.route('/api/reset-data', methods=['POST'])
@login_required
@admin_required
def reset_data():
    """Réinitialiser sélectivement les données"""
    try:
        from backend.config.database import get_db_connection
        
        data = request.json
        reset_reservations = data.get('reset_reservations', False)
        reset_chambres = data.get('reset_chambres', False)
        reset_etablissements = data.get('reset_etablissements', False)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            if reset_reservations:
                cur.execute("DELETE FROM reservations_chambres")
                cur.execute("DELETE FROM personnes")
                cur.execute("DELETE FROM reservations")
            
            if reset_chambres:
                if not reset_reservations:
                    cur.execute("DELETE FROM reservations_chambres")
                cur.execute("DELETE FROM chambres")
            
            if reset_etablissements:
                cur.execute("DELETE FROM etablissements WHERE nom_etablissement != 'Maison d''Hôte'")
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Données réinitialisées avec succès'})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@data_bp.route('/api/reset-all-data', methods=['POST'])
@login_required
@admin_required
def reset_all_data():
    """Réinitialiser toutes les données"""
    try:
        from backend.config.database import get_db_connection
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("DELETE FROM reservations_chambres")
            cur.execute("DELETE FROM personnes")
            cur.execute("DELETE FROM reservations")
            cur.execute("DELETE FROM chambres")
            cur.execute("DELETE FROM etablissements WHERE id != 1")
            cur.execute("DELETE FROM parametres_systeme WHERE id != 1")
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Toutes les données ont été réinitialisées'})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
