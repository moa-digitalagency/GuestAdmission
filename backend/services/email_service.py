"""
Service pour la gestion des emails (envoi SMTP et réception POP3)
"""
import smtplib
import poplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from typing import Dict, List, Optional
from ..config.database import get_db_connection
from ..models.mail_config import MailConfig


class EmailService:
    """Service pour gérer l'envoi et la réception d'emails"""
    
    @staticmethod
    def send_email(config_id: int, to_email: str, subject: str, body_html: str, 
                   cc_email: Optional[str] = None, bcc_email: Optional[str] = None) -> bool:
        """Envoyer un email via SMTP"""
        config = MailConfig.get_by_id(config_id)
        if not config:
            raise ValueError("Configuration mail non trouvée")
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = config['email_address']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc_email:
                msg['Cc'] = cc_email
            
            msg.attach(MIMEText(body_html, 'html'))
            
            recipients = [to_email]
            if cc_email:
                recipients.extend([email.strip() for email in cc_email.split(',')])
            if bcc_email:
                recipients.extend([email.strip() for email in bcc_email.split(',')])
            
            if config['smtp_use_tls']:
                with smtplib.SMTP(config['smtp_host'], config['smtp_port']) as server:
                    server.starttls()
                    server.login(config['smtp_username'], config['smtp_password'])
                    server.sendmail(config['email_address'], recipients, msg.as_string())
            else:
                with smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port']) as server:
                    server.login(config['smtp_username'], config['smtp_password'])
                    server.sendmail(config['email_address'], recipients, msg.as_string())
            
            EmailService._save_sent_email(
                config_id=config_id,
                to_email=to_email,
                cc_email=cc_email,
                bcc_email=bcc_email,
                subject=subject,
                body_html=body_html
            )
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            raise
    
    @staticmethod
    def fetch_emails(config_id: int, limit: int = 50) -> List[Dict]:
        """Récupérer les emails via POP3"""
        config = MailConfig.get_by_id(config_id)
        if not config or not config.get('pop_host'):
            raise ValueError("Configuration POP3 non trouvée ou incomplète")
        
        try:
            if config['pop_use_ssl']:
                server = poplib.POP3_SSL(config['pop_host'], config['pop_port'])
            else:
                server = poplib.POP3(config['pop_host'], config['pop_port'])
            
            server.user(config['pop_username'])
            server.pass_(config['pop_password'])
            
            num_messages = len(server.list()[1])
            emails_data = []
            
            start = max(1, num_messages - limit + 1)
            for i in range(start, num_messages + 1):
                try:
                    response, lines, octets = server.retr(i)
                    msg_content = b'\r\n'.join(lines).decode('utf-8', errors='ignore')
                    msg = email.message_from_string(msg_content)
                    
                    subject = EmailService._decode_header_value(msg.get('Subject', ''))
                    from_email = EmailService._decode_header_value(msg.get('From', ''))
                    to_email = EmailService._decode_header_value(msg.get('To', ''))
                    date_str = msg.get('Date', '')
                    message_id = msg.get('Message-ID', f'local-{i}')
                    
                    body_text = ''
                    body_html = ''
                    
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == 'text/plain':
                                body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            elif content_type == 'text/html':
                                body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body_text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    
                    email_data = {
                        'message_id': message_id,
                        'subject': subject,
                        'from_email': from_email,
                        'to_email': to_email,
                        'body_text': body_text,
                        'body_html': body_html,
                        'date_sent': date_str,
                        'folder': 'inbox'
                    }
                    
                    EmailService._save_received_email(config_id, email_data)
                    emails_data.append(email_data)
                    
                except Exception as e:
                    print(f"Erreur lors de la lecture du message {i}: {e}")
                    continue
            
            server.quit()
            return emails_data
            
        except Exception as e:
            print(f"Erreur lors de la récupération des emails: {e}")
            raise
    
    @staticmethod
    def get_emails_by_folder(config_id: int, folder: str = 'inbox', limit: int = 100) -> List[Dict]:
        """Récupérer les emails stockés par dossier"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT * FROM emails 
            WHERE mail_config_id = %s AND folder = %s
            ORDER BY date_received DESC
            LIMIT %s
        ''', (config_id, folder, limit))
        
        emails = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(email) for email in emails] if emails else []
    
    @staticmethod
    def get_email_by_id(email_id: int) -> Optional[Dict]:
        """Récupérer un email par son ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM emails WHERE id = %s', (email_id,))
        email_data = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(email_data) if email_data else None
    
    @staticmethod
    def mark_as_read(email_id: int):
        """Marquer un email comme lu"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('UPDATE emails SET is_read = TRUE WHERE id = %s', (email_id,))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def move_to_folder(email_id: int, folder: str):
        """Déplacer un email vers un dossier"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('UPDATE emails SET folder = %s WHERE id = %s', (folder, email_id))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def delete_email(email_id: int):
        """Supprimer un email"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM emails WHERE id = %s', (email_id,))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def _save_sent_email(config_id: int, to_email: str, subject: str, body_html: str,
                        cc_email: Optional[str] = None, bcc_email: Optional[str] = None):
        """Enregistrer un email envoyé dans la base de données"""
        config = MailConfig.get_by_id(config_id)
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO emails (
                mail_config_id, subject, from_email, to_email, cc_email, bcc_email,
                body_html, folder, is_read, date_sent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            config_id,
            subject,
            config['email_address'],
            to_email,
            cc_email,
            bcc_email,
            body_html,
            'sent',
            True,
            datetime.now()
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def _save_received_email(config_id: int, email_data: Dict):
        """Enregistrer un email reçu dans la base de données"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT id FROM emails WHERE message_id = %s
        ''', (email_data['message_id'],))
        
        existing = cur.fetchone()
        
        if not existing:
            cur.execute('''
                INSERT INTO emails (
                    mail_config_id, message_id, subject, from_email, to_email,
                    body_text, body_html, folder, date_sent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                config_id,
                email_data['message_id'],
                email_data['subject'],
                email_data['from_email'],
                email_data['to_email'],
                email_data['body_text'],
                email_data['body_html'],
                email_data['folder'],
                email_data.get('date_sent')
            ))
            
            conn.commit()
        
        cur.close()
        conn.close()
    
    @staticmethod
    def _decode_header_value(value: str) -> str:
        """Décoder les valeurs d'en-tête encodées"""
        if not value:
            return ''
        
        decoded_parts = decode_header(value)
        decoded_value = ''
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_value += part.decode(encoding or 'utf-8', errors='ignore')
                except:
                    decoded_value += part.decode('utf-8', errors='ignore')
            else:
                decoded_value += part
        
        return decoded_value
    
    @staticmethod
    def index_client_email(email_id: int, client_email: str):
        """Indexer un email avec un contact client"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE emails 
            SET client_email_indexed = %s 
            WHERE id = %s
        ''', (client_email, email_id))
        
        conn.commit()
        cur.close()
        conn.close()
