"""
Service pour la gestion des calendriers iCal (Airbnb, Booking.com, etc.)
"""
from typing import List, Dict, Optional
from datetime import datetime
from icalendar import Calendar
import requests
from urllib.parse import urlparse
from ..config.database import get_db_connection
from ..utils import serialize_rows


class CalendarService:
    """Service pour gérer les calendriers iCal externes"""
    
    @staticmethod
    def _validate_ical_url(url: str) -> bool:
        """Valider l'URL iCal pour éviter les risques SSRF"""
        try:
            parsed = urlparse(url)
            
            if parsed.scheme not in ['http', 'https']:
                return False
            
            if not parsed.netloc:
                return False
            
            blocked_hosts = [
                'localhost', '127.0.0.1', '0.0.0.0',
                '169.254.169.254',
                '::1', 'localhost.localdomain'
            ]
            
            host_lower = parsed.netloc.lower().split(':')[0]
            if host_lower in blocked_hosts:
                return False
            
            if host_lower.startswith('192.168.') or host_lower.startswith('10.') or host_lower.startswith('172.'):
                if host_lower.startswith('172.'):
                    octets = host_lower.split('.')
                    if len(octets) >= 2:
                        try:
                            second_octet = int(octets[1])
                            if 16 <= second_octet <= 31:
                                return False
                        except ValueError:
                            pass
                else:
                    return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def create_calendar(data: Dict) -> Optional[int]:
        """Créer un nouveau calendrier iCal"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO calendriers_ical (
                etablissement_id, nom, plateforme, ical_url, actif
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('etablissement_id'),
            data.get('nom'),
            data.get('plateforme', 'autre'),
            data.get('ical_url'),
            data.get('actif', True)
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return result['id'] if result else None
    
    @staticmethod
    def get_all_calendars(etablissement_id: Optional[int] = None) -> List[Dict]:
        """Récupérer tous les calendriers"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = '''
            SELECT c.*, e.nom_etablissement
            FROM calendriers_ical c
            LEFT JOIN etablissements e ON c.etablissement_id = e.id
            WHERE 1=1
        '''
        params = []
        
        if etablissement_id:
            query += ' AND c.etablissement_id = %s'
            params.append(etablissement_id)
        
        query += ' ORDER BY c.created_at DESC'
        
        cur.execute(query, tuple(params))
        calendars = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return serialize_rows(calendars)
    
    @staticmethod
    def get_calendar_by_id(calendar_id: int) -> Optional[Dict]:
        """Récupérer un calendrier par son ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM calendriers_ical WHERE id = %s', (calendar_id,))
        calendar = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(calendar) if calendar else None
    
    @staticmethod
    def update_calendar(calendar_id: int, data: Dict) -> bool:
        """Mettre à jour un calendrier"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE calendriers_ical SET
                nom = %s, plateforme = %s, ical_url = %s, actif = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (
            data.get('nom'),
            data.get('plateforme'),
            data.get('ical_url'),
            data.get('actif'),
            calendar_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
    
    @staticmethod
    def delete_calendar(calendar_id: int) -> bool:
        """Supprimer un calendrier"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM calendriers_ical WHERE id = %s', (calendar_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
    
    @staticmethod
    def synchronize_calendar(calendar_id: int) -> Dict:
        """Synchroniser un calendrier avec sa source iCal"""
        calendar = CalendarService.get_calendar_by_id(calendar_id)
        if not calendar:
            return {'success': False, 'message': 'Calendrier non trouvé'}
        
        if not CalendarService._validate_ical_url(calendar['ical_url']):
            return {'success': False, 'message': 'URL non autorisée (sécurité SSRF)'}
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            response = requests.get(calendar['ical_url'], timeout=30)
            response.raise_for_status()
            
            ical_data = Calendar.from_ical(response.text)
            
            sejours_count = 0
            errors = []
            
            for component in ical_data.walk():
                if component.name == "VEVENT":
                    try:
                        uid = str(component.get('uid', ''))
                        summary = str(component.get('summary', 'Séjour'))
                        dtstart = component.get('dtstart')
                        dtend = component.get('dtend')
                        description = str(component.get('description', ''))
                        
                        if dtstart and dtend:
                            date_debut = dtstart.dt if hasattr(dtstart.dt, 'date') else dtstart.dt
                            date_fin = dtend.dt if hasattr(dtend.dt, 'date') else dtend.dt
                            
                            if isinstance(date_debut, datetime):
                                date_debut = date_debut.date()
                            if isinstance(date_fin, datetime):
                                date_fin = date_fin.date()
                            
                            cur.execute('''
                                INSERT INTO reservations_ical (
                                    calendrier_id, uid_ical, titre, date_debut, date_fin, description
                                ) VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (uid_ical) DO UPDATE SET
                                    titre = EXCLUDED.titre,
                                    date_debut = EXCLUDED.date_debut,
                                    date_fin = EXCLUDED.date_fin,
                                    description = EXCLUDED.description,
                                    updated_at = CURRENT_TIMESTAMP
                            ''', (calendar_id, uid, summary, date_debut, date_fin, description))
                            
                            sejours_count += 1
                    except Exception as e:
                        errors.append(f"Erreur événement: {str(e)}")
            
            cur.execute('''
                UPDATE calendriers_ical SET
                    derniere_synchronisation = CURRENT_TIMESTAMP,
                    statut_derniere_synchro = %s,
                    message_erreur = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', ('succès' if sejours_count > 0 else 'aucune_sejour', 
                  '\n'.join(errors) if errors else None, calendar_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'success': True,
                'message': f'{sejours_count} séjour(s) synchronisée(s)',
                'count': sejours_count,
                'errors': errors
            }
            
        except requests.exceptions.RequestException as e:
            cur.execute('''
                UPDATE calendriers_ical SET
                    derniere_synchronisation = CURRENT_TIMESTAMP,
                    statut_derniere_synchro = 'erreur',
                    message_erreur = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (f"Erreur de connexion: {str(e)}", calendar_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': False, 'message': f'Erreur de connexion: {str(e)}'}
        
        except Exception as e:
            cur.execute('''
                UPDATE calendriers_ical SET
                    derniere_synchronisation = CURRENT_TIMESTAMP,
                    statut_derniere_synchro = 'erreur',
                    message_erreur = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (f"Erreur de parsing: {str(e)}", calendar_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': False, 'message': f'Erreur de parsing: {str(e)}'}
    
    @staticmethod
    def get_calendar_sejours(calendar_id: int) -> List[Dict]:
        """Récupérer les séjours d'un calendrier"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT * FROM reservations_ical
            WHERE calendrier_id = %s
            ORDER BY date_debut DESC
        ''', (calendar_id,))
        
        sejours = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return serialize_rows(sejours)
    
    @staticmethod
    def get_all_ical_sejours(etablissement_id: Optional[int] = None, 
                                   date_debut: Optional[str] = None,
                                   date_fin: Optional[str] = None) -> List[Dict]:
        """Récupérer toutes les séjours iCal avec filtres"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = '''
            SELECT r.*, c.nom as calendrier_nom, c.plateforme
            FROM reservations_ical r
            JOIN calendriers_ical c ON r.calendrier_id = c.id
            WHERE c.actif = TRUE
        '''
        params = []
        
        if etablissement_id:
            query += ' AND c.etablissement_id = %s'
            params.append(etablissement_id)
        
        if date_debut:
            query += ' AND r.date_fin >= %s'
            params.append(date_debut)
        
        if date_fin:
            query += ' AND r.date_debut <= %s'
            params.append(date_fin)
        
        query += ' ORDER BY r.date_debut'
        
        cur.execute(query, tuple(params))
        sejours = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return serialize_rows(sejours)
