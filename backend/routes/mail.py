"""
Routes pour la gestion de la messagerie
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..models.mail_config import MailConfig
from ..services.email_service import EmailService

mail_bp = Blueprint('mail', __name__)


def verify_config_access(config_id, etablissement_id):
    """Vérifier que l'utilisateur a accès à cette configuration mail"""
    if not etablissement_id:
        return None, ('Établissement requis pour accéder à cette ressource', 400)
    
    config = MailConfig.get_by_id(config_id)
    if not config:
        return None, ('Configuration non trouvée', 404)
    
    if config['etablissement_id'] != etablissement_id:
        return None, ('Accès non autorisé à cette configuration', 403)
    
    return config, None


@mail_bp.route('/api/mail-configs', methods=['GET'])
@login_required
def get_mail_configs():
    """Récupérer toutes les configurations mail"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    
    if not etablissement_id:
        return jsonify({'error': 'Établissement requis'}), 400
    
    configs = MailConfig.get_all(etablissement_id)
    
    for config in configs:
        del config['smtp_password']
        if 'pop_password' in config:
            del config['pop_password']
    
    return jsonify(configs)


@mail_bp.route('/api/mail-configs/<int:config_id>', methods=['GET'])
@login_required
def get_mail_config(config_id):
    """Récupérer une configuration mail par ID"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    
    config, error = verify_config_access(config_id, etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
    del config['smtp_password']
    if 'pop_password' in config:
        del config['pop_password']
    return jsonify(config)


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
    etablissement_id = data.get('etablissement_id')
    
    config, error = verify_config_access(config_id, etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
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
    etablissement_id = request.args.get('etablissement_id', type=int)
    
    config, error = verify_config_access(config_id, etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
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
    etablissement_id = data.get('etablissement_id')
    to_email = data.get('to_email')
    subject = data.get('subject')
    body_html = data.get('body_html')
    cc_email = data.get('cc_email')
    bcc_email = data.get('bcc_email')
    
    if not all([config_id, to_email, subject, body_html]):
        return jsonify({'error': 'Données manquantes'}), 400
    
    config, error = verify_config_access(config_id, etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
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
    etablissement_id = request.args.get('etablissement_id', type=int)
    
    config, error = verify_config_access(config_id, etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
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
    etablissement_id = request.args.get('etablissement_id', type=int)
    
    config, error = verify_config_access(config_id, etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
    try:
        emails = EmailService.get_emails_by_folder(config_id, folder, limit)
        return jsonify(emails)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail/email/<int:email_id>', methods=['GET'])
@login_required
def get_email(email_id):
    """Récupérer un email par son ID"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    
    if not etablissement_id:
        return jsonify({'error': 'Établissement requis'}), 400
    
    email_data = EmailService.get_email_by_id(email_id)
    if not email_data:
        return jsonify({'error': 'Email non trouvé'}), 404
    
    config, error = verify_config_access(email_data['mail_config_id'], etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
    EmailService.mark_as_read(email_id)
    return jsonify(email_data)


@mail_bp.route('/api/mail/email/<int:email_id>/read', methods=['POST'])
@login_required
def mark_email_read(email_id):
    """Marquer un email comme lu"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    
    if not etablissement_id:
        return jsonify({'error': 'Établissement requis'}), 400
    
    email_data = EmailService.get_email_by_id(email_id)
    if not email_data:
        return jsonify({'error': 'Email non trouvé'}), 404
    
    config, error = verify_config_access(email_data['mail_config_id'], etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
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
    etablissement_id = data.get('etablissement_id')
    
    if not folder:
        return jsonify({'error': 'Dossier non spécifié'}), 400
    
    if not etablissement_id:
        return jsonify({'error': 'Établissement requis'}), 400
    
    email_data = EmailService.get_email_by_id(email_id)
    if not email_data:
        return jsonify({'error': 'Email non trouvé'}), 404
    
    config, error = verify_config_access(email_data['mail_config_id'], etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
    try:
        EmailService.move_to_folder(email_id, folder)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mail_bp.route('/api/mail/email/<int:email_id>', methods=['DELETE'])
@login_required
def delete_email(email_id):
    """Supprimer un email"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    
    if not etablissement_id:
        return jsonify({'error': 'Établissement requis'}), 400
    
    email_data = EmailService.get_email_by_id(email_id)
    if not email_data:
        return jsonify({'error': 'Email non trouvé'}), 404
    
    config, error = verify_config_access(email_data['mail_config_id'], etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
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
    etablissement_id = data.get('etablissement_id')
    
    if not client_email:
        return jsonify({'error': 'Email client non spécifié'}), 400
    
    if not etablissement_id:
        return jsonify({'error': 'Établissement requis'}), 400
    
    email_data = EmailService.get_email_by_id(email_id)
    if not email_data:
        return jsonify({'error': 'Email non trouvé'}), 404
    
    config, error = verify_config_access(email_data['mail_config_id'], etablissement_id)
    if error:
        return jsonify({'error': error[0]}), error[1]
    
    try:
        EmailService.index_client_email(email_id, client_email)
        return jsonify({
            'success': True,
            'message': 'Email indexé avec le contact client'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
