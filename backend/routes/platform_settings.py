from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models.platform_settings import PlatformSettings
from ..decorators.roles import platform_admin_required

platform_settings_bp = Blueprint('platform_settings', __name__)


@platform_settings_bp.route('/api/platform-settings', methods=['GET'])
@login_required
@platform_admin_required
def get_platform_settings():
    """Récupérer les paramètres de la plateforme (PLATFORM_ADMIN seulement)"""
    try:
        settings = PlatformSettings.get_settings()
        
        if not settings:
            return jsonify({
                'success': False,
                'error': 'Paramètres non trouvés'
            }), 404
        
        return jsonify({
            'success': True,
            'settings': dict(settings)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@platform_settings_bp.route('/api/platform-settings', methods=['PUT'])
@login_required
@platform_admin_required
def update_platform_settings():
    """Mettre à jour les paramètres de la plateforme (PLATFORM_ADMIN seulement)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400
        
        PlatformSettings.update_settings(data)
        
        return jsonify({
            'success': True,
            'message': 'Paramètres mis à jour avec succès'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@platform_settings_bp.route('/api/platform-settings/public', methods=['GET'])
def get_public_platform_settings():
    """Récupérer les paramètres publics de la plateforme (accessible à tous)"""
    try:
        settings = PlatformSettings.get_public_settings()
        
        if not settings:
            return jsonify({
                'success': True,
                'settings': {
                    'platform_name': 'Maison d\'Hôte',
                    'default_currency': 'MAD',
                    'default_language': 'fr'
                }
            })
        
        return jsonify({
            'success': True,
            'settings': dict(settings)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
