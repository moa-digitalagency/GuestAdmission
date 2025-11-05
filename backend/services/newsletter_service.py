import os
import requests
from backend.models.newsletter import Newsletter, NewsletterConfig
import markdown
import logging

logger = logging.getLogger(__name__)


class NewsletterService:
    """Service pour l'envoi de newsletters via SendGrid"""
    
    @staticmethod
    def send_newsletter(etablissement_id, subject, content, content_type, recipient_emails, sent_by_user_id):
        """
        Envoyer une newsletter à plusieurs destinataires
        
        Args:
            etablissement_id: ID de l'établissement
            subject: Sujet de l'email
            content: Contenu (markdown ou HTML)
            content_type: Type de contenu ('markdown' ou 'html')
            recipient_emails: Liste des emails destinataires
            sent_by_user_id: ID de l'utilisateur qui envoie
        
        Returns:
            dict avec success et message
        """
        try:
            config = NewsletterConfig.get_by_etablissement(etablissement_id)
            
            if not config:
                return {
                    'success': False,
                    'error': 'Configuration SendGrid non trouvée. Veuillez configurer SendGrid dans les paramètres.'
                }
            
            newsletter_id = Newsletter.create(
                etablissement_id=etablissement_id,
                subject=subject,
                content=content,
                content_type=content_type,
                recipient_emails=recipient_emails,
                sent_by_user_id=sent_by_user_id
            )
            
            html_content = content
            if content_type == 'markdown':
                html_content = markdown.markdown(content)
            
            html_content = NewsletterService._wrap_html_template(html_content, subject, config.get('from_name', ''))
            
            result = NewsletterService._send_via_sendgrid(
                api_key=config['sendgrid_api_key'],
                from_email=config['from_email'],
                from_name=config.get('from_name', config['from_email']),
                to_emails=recipient_emails,
                subject=subject,
                html_content=html_content
            )
            
            if result['success']:
                Newsletter.update_status(newsletter_id, 'sent')
                return {
                    'success': True,
                    'message': f'Newsletter envoyée avec succès à {len(recipient_emails)} destinataire(s)',
                    'newsletter_id': newsletter_id
                }
            else:
                Newsletter.update_status(newsletter_id, 'failed', result.get('error'))
                return {
                    'success': False,
                    'error': result.get('error', 'Erreur lors de l\'envoi')
                }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la newsletter: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur: {str(e)}'
            }
    
    @staticmethod
    def _send_via_sendgrid(api_key, from_email, from_name, to_emails, subject, html_content):
        """Envoyer un email via l'API SendGrid"""
        try:
            url = 'https://api.sendgrid.com/v3/mail/send'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            personalizations = []
            for email in to_emails:
                personalizations.append({
                    'to': [{'email': email}]
                })
            
            data = {
                'personalizations': personalizations,
                'from': {
                    'email': from_email,
                    'name': from_name
                },
                'subject': subject,
                'content': [{
                    'type': 'text/html',
                    'value': html_content
                }]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code in [200, 202]:
                return {'success': True}
            else:
                error_message = f'SendGrid API error: {response.status_code} - {response.text}'
                logger.error(error_message)
                return {'success': False, 'error': error_message}
        
        except Exception as e:
            logger.error(f"Erreur lors de l'appel SendGrid: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _wrap_html_template(content, subject, from_name):
        """Envelopper le contenu dans un template HTML responsive"""
        return f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #1a1a1a;
        }}
        a {{
            color: #3b82f6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 0.875rem;
            color: #6b7280;
            text-align: center;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        {content}
        <div class="footer">
            <p>Envoyé par {from_name}</p>
        </div>
    </div>
</body>
</html>
'''
    
    @staticmethod
    def test_configuration(api_key, from_email, from_name):
        """Tester la configuration SendGrid"""
        try:
            result = NewsletterService._send_via_sendgrid(
                api_key=api_key,
                from_email=from_email,
                from_name=from_name,
                to_emails=[from_email],
                subject='Test de configuration SendGrid',
                html_content='<p>Ceci est un email de test. Votre configuration SendGrid fonctionne correctement!</p>'
            )
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
