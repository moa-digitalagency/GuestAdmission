from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user
from backend.decorators.roles import tenant_admin_required
from backend.models.newsletter import Newsletter, NewsletterConfig
from backend.models.client import Client
from backend.services.newsletter_service import NewsletterService
from backend.utils.tenant_context import get_current_etablissement_id

newsletters_bp = Blueprint('newsletters', __name__)


@newsletters_bp.route('/newsletters')
@tenant_admin_required
def newsletters_page():
    """Page de gestion des newsletters"""
    return render_template('newsletters.html')


@newsletters_bp.route('/api/newsletters', methods=['GET'])
@tenant_admin_required
def get_newsletters():
    """Récupérer l'historique des newsletters"""
    try:
        etablissement_id = get_current_etablissement_id()
        if not etablissement_id:
            return jsonify({'success': False, 'error': 'Établissement non trouvé'}), 400
        newsletters = Newsletter.get_by_etablissement(etablissement_id)
        return jsonify({
            'success': True,
            'newsletters': newsletters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@newsletters_bp.route('/api/newsletters/send', methods=['POST'])
@tenant_admin_required
def send_newsletter():
    """Envoyer une newsletter"""
    try:
        data = request.get_json()
        etablissement_id = get_current_etablissement_id()
        
        if not etablissement_id:
            return jsonify({'success': False, 'error': 'Établissement non trouvé'}), 400
        
        user_id = current_user.id
        
        subject = data.get('subject', '').strip()
        content = data.get('content', '').strip()
        content_type = data.get('content_type', 'html')
        recipient_emails = data.get('recipient_emails', [])
        
        if not subject:
            return jsonify({
                'success': False,
                'error': 'Le sujet est obligatoire'
            }), 400
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Le contenu est obligatoire'
            }), 400
        
        if not recipient_emails or len(recipient_emails) == 0:
            return jsonify({
                'success': False,
                'error': 'Aucun destinataire sélectionné'
            }), 400
        
        result = NewsletterService.send_newsletter(
            etablissement_id=etablissement_id,
            subject=subject,
            content=content,
            content_type=content_type,
            recipient_emails=recipient_emails,
            sent_by_user_id=user_id
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@newsletters_bp.route('/api/newsletters/config', methods=['GET'])
@tenant_admin_required
def get_newsletter_config():
    """Récupérer la configuration SendGrid"""
    try:
        etablissement_id = get_current_etablissement_id()
        if not etablissement_id:
            return jsonify({'success': False, 'error': 'Établissement non trouvé'}), 400
        config = NewsletterConfig.get_by_etablissement(etablissement_id)
        
        if config:
            return jsonify({
                'success': True,
                'config': {
                    'from_email': config.get('from_email'),
                    'from_name': config.get('from_name'),
                    'active': config.get('active', False),
                    'has_api_key': bool(config.get('sendgrid_api_key'))
                }
            })
        else:
            return jsonify({
                'success': True,
                'config': None
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@newsletters_bp.route('/api/newsletters/config', methods=['POST'])
@tenant_admin_required
def save_newsletter_config():
    """Sauvegarder la configuration SendGrid"""
    try:
        data = request.get_json()
        etablissement_id = get_current_etablissement_id()
        if not etablissement_id:
            return jsonify({'success': False, 'error': 'Établissement non trouvé'}), 400
        
        sendgrid_api_key = data.get('sendgrid_api_key', '').strip()
        from_email = data.get('from_email', '').strip()
        from_name = data.get('from_name', '').strip()
        
        if not sendgrid_api_key or not from_email:
            return jsonify({
                'success': False,
                'error': 'La clé API SendGrid et l\'email expéditeur sont obligatoires'
            }), 400
        
        test_result = NewsletterService.test_configuration(
            api_key=sendgrid_api_key,
            from_email=from_email,
            from_name=from_name or from_email
        )
        
        if not test_result.get('success'):
            return jsonify({
                'success': False,
                'error': f'La configuration SendGrid est invalide: {test_result.get("error")}'
            }), 400
        
        NewsletterConfig.create_or_update(
            etablissement_id=etablissement_id,
            sendgrid_api_key=sendgrid_api_key,
            from_email=from_email,
            from_name=from_name
        )
        
        return jsonify({
            'success': True,
            'message': 'Configuration SendGrid enregistrée et testée avec succès'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@newsletters_bp.route('/api/newsletters/clients', methods=['GET'])
@tenant_admin_required
def get_newsletter_clients():
    """Récupérer les clients pour la sélection"""
    try:
        etablissement_id = get_current_etablissement_id()
        if not etablissement_id:
            return jsonify({'success': False, 'error': 'Établissement non trouvé'}), 400
        clients = Client.get_all_by_etablissement(etablissement_id)
        
        client_list = []
        for client in clients:
            if client.get('email'):
                client_list.append({
                    'id': client.get('id'),
                    'nom': client.get('nom', ''),
                    'prenom': client.get('prenom', ''),
                    'email': client.get('email'),
                    'pays': client.get('pays', ''),
                    'ville': client.get('ville', '')
                })
        
        return jsonify({
            'success': True,
            'clients': client_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
