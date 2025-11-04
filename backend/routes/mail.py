"""
Routes pour la gestion de la messagerie
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..models.mail_config import MailConfig
from ..services.email_service import EmailService

mail_bp = Blueprint('mail', __name__)


@mail_bp.route('/api/mail-configs', methods=['GET'])
@login_required
def get_mail_configs():
    """Récupérer toutes les configurations mail"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    configs = MailConfig.get_all(etablissement_id)
    
    for config in configs:
        config['smtp_password'] = '***'
        if config.get('pop_password'):
            config['pop_password'] = '***'
    
    return jsonify(configs)


@mail_bp.route('/api/mail-configs/<int:config_id>', methods=['GET'])
@login_required
def get_mail_config(config_id):
    """Récupérer une configuration mail par ID"""
    config = MailConfig.get_by_id(config_id)
    if config:
        config['smtp_password'] = '***'
        if config.get('pop_password'):
            config['pop_password'] = '***'
        return jsonify(config)
    return jsonify({'error': 'Configuration non trouvée'}), 404


@mail_bp.route('/api/mail-configs', methods=['POST'])
@login_required
def create_mail_config():
    """Créer une nouvelle configuration mail"""
    data = request.get_json()
    
    try:
        config_id = MailConfig.create(data)
        return jsonify({
            'success': True,
            'config_id': config_id,
            'message': 'Configuration mail créée avec succès'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail-configs/<int:config_id>', methods=['PUT'])
@login_required
def update_mail_config(config_id):
    """Mettre à jour une configuration mail"""
    data = request.get_json()
    
    try:
        MailConfig.update(config_id, data)
        return jsonify({
            'success': True,
            'message': 'Configuration mail mise à jour avec succès'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail-configs/<int:config_id>', methods=['DELETE'])
@login_required
def delete_mail_config(config_id):
    """Supprimer une configuration mail"""
    try:
        MailConfig.delete(config_id)
        return jsonify({
            'success': True,
            'message': 'Configuration mail supprimée avec succès'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail/send', methods=['POST'])
@login_required
def send_email():
    """Envoyer un email"""
    data = request.get_json()
    
    config_id = data.get('config_id')
    to_email = data.get('to_email')
    subject = data.get('subject')
    body_html = data.get('body_html')
    cc_email = data.get('cc_email')
    bcc_email = data.get('bcc_email')
    
    if not all([config_id, to_email, subject, body_html]):
        return jsonify({'error': 'Données manquantes'}), 400
    
    try:
        EmailService.send_email(
            config_id=config_id,
            to_email=to_email,
            subject=subject,
            body_html=body_html,
            cc_email=cc_email,
            bcc_email=bcc_email
        )
        
        client_email_indexed = data.get('client_email_indexed')
        if client_email_indexed:
            pass
        
        return jsonify({
            'success': True,
            'message': 'Email envoyé avec succès'
        })
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'envoi: {str(e)}'}), 500


@mail_bp.route('/api/mail/fetch/<int:config_id>', methods=['POST'])
@login_required
def fetch_emails(config_id):
    """Récupérer les emails via POP3"""
    limit = request.args.get('limit', 50, type=int)
    
    try:
        emails = EmailService.fetch_emails(config_id, limit)
        return jsonify({
            'success': True,
            'count': len(emails),
            'message': f'{len(emails)} email(s) récupéré(s)'
        })
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500


@mail_bp.route('/api/mail/emails/<int:config_id>', methods=['GET'])
@login_required
def get_emails(config_id):
    """Récupérer les emails d'un dossier"""
    folder = request.args.get('folder', 'inbox')
    limit = request.args.get('limit', 100, type=int)
    
    try:
        emails = EmailService.get_emails_by_folder(config_id, folder, limit)
        return jsonify(emails)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail/email/<int:email_id>', methods=['GET']])
@login_required
def get_email(email_id):
    """Récupérer un email par son ID"""
    email_data = EmailService.get_email_by_id(email_id)
    if email_data:
        EmailService.mark_as_read(email_id)
        return jsonify(email_data)
    return jsonify({'error': 'Email non trouvé'}), 404


@mail_bp.route('/api/mail/email/<int:email_id>/read', methods=['POST'])
@login_required
def mark_email_read(email_id):
    """Marquer un email comme lu"""
    try:
        EmailService.mark_as_read(email_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail/email/<int:email_id>/move', methods=['POST'])
@login_required
def move_email(email_id):
    """Déplacer un email vers un dossier"""
    data = request.get_json()
    folder = data.get('folder')
    
    if not folder:
        return jsonify({'error': 'Dossier non spécifié'}), 400
    
    try:
        EmailService.move_to_folder(email_id, folder)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail/email/<int:email_id>', methods=['DELETE'])
@login_required
def delete_email(email_id):
    """Supprimer un email"""
    try:
        EmailService.delete_email(email_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail/email/<int:email_id>/index-client', methods=['POST'])
@login_required
def index_client_email(email_id):
    """Indexer un email avec un contact client"""
    data = request.get_json()
    client_email = data.get('client_email')
    
    if not client_email:
        return jsonify({'error': 'Email client non spécifié'}), 400
    
    try:
        EmailService.index_client_email(email_id, client_email)
        return jsonify({
            'success': True,
            'message': 'Email indexé avec le contact client'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
