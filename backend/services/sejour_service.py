"""
Service pour la gestion des séjours
"""
from typing import List, Dict, Optional, Any
from ..config.database import get_db_connection
from ..models.reservation import Reservation
from ..models.personne import Personne
from ..utils import serialize_rows, serialize_row
from datetime import datetime


class SejourService:
    """Service pour gérer les opérations sur les séjours"""
    
    @staticmethod
    def get_all_sejours(etablissement_id: Optional[int] = None, statut: Optional[str] = None) -> List[Dict]:
        """Récupérer tous les séjours avec filtres optionnels"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = '''
            SELECT r.*, 
                   e.nom_etablissement,
                   p.nom as contact_nom, 
                   p.prenom as contact_prenom,
                   p.email as contact_email,
                   p.telephone as contact_telephone
            FROM reservations r
            LEFT JOIN etablissements e ON r.etablissement_id = e.id
            LEFT JOIN personnes p ON r.id = p.reservation_id AND p.est_contact_principal = TRUE
            WHERE 1=1
        '''
        params = []
        
        if etablissement_id:
            query += ' AND r.etablissement_id = %s'
            params.append(etablissement_id)
        
        if statut:
            query += ' AND r.statut = %s'
            params.append(statut)
        
        query += ' ORDER BY r.created_at DESC'
        
        cur.execute(query, tuple(params))
        sejours = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return serialize_rows(sejours)
    
    @staticmethod
    def get_sejour_details(sejour_id: int) -> Optional[Dict]:
        """Récupérer les détails complets d'un séjour"""
        sejour = Reservation.get_by_id(sejour_id)
        if not sejour:
            return None
        
        personnes = Personne.get_by_reservation(sejour_id)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Récupérer les chambres
        cur.execute('''
            SELECT c.id, c.nom, c.description, c.capacite, c.prix_par_nuit
            FROM chambres c
            JOIN reservations_chambres rc ON c.id = rc.chambre_id
            WHERE rc.reservation_id = %s
        ''', (sejour_id,))
        chambres = cur.fetchall()
        
        # Récupérer l'établissement
        cur.execute('''
            SELECT * FROM etablissements WHERE id = (
                SELECT etablissement_id FROM reservations WHERE id = %s
            )
        ''', (sejour_id,))
        etablissement = cur.fetchone()
        
        # Récupérer les extras associés
        cur.execute('''
            SELECT e.*, se.quantite, se.montant_total, se.date_ajout
            FROM extras e
            JOIN sejours_extras se ON e.id = se.extra_id
            WHERE se.sejour_id = %s
            ORDER BY se.date_ajout DESC
        ''', (sejour_id,))
        extras = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            'sejour': serialize_row(sejour),
            'personnes': serialize_rows(personnes),
            'chambres': [dict(c) for c in chambres] if chambres else [],
            'etablissement': dict(etablissement) if etablissement else None,
            'extras': [dict(e) for e in extras] if extras else []
        }
    
    @staticmethod
    def create_sejour(data: Dict) -> Optional[int]:
        """Créer un nouveau séjour"""
        sejour_data = data.get('sejour', {}) or data.get('reservation', {})
        personnes_data = data.get('personnes', [])
        chambres_ids = data.get('chambres', [])
        
        sejour_id = Reservation.create(sejour_data)
        
        if sejour_id:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Associer les chambres
            if chambres_ids:
                for chambre_id in chambres_ids:
                    cur.execute('''
                        INSERT INTO reservations_chambres (reservation_id, chambre_id)
                        VALUES (%s, %s)
                    ''', (sejour_id, chambre_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            # Créer les personnes
            if personnes_data:
                for i, personne_data in enumerate(personnes_data):
                    personne_data['reservation_id'] = sejour_id
                    personne_data['est_contact_principal'] = (i == 0)
                    Personne.create(personne_data)
        
        return sejour_id
    
    @staticmethod
    def get_sejours_by_filters(filters: Dict) -> List[Dict]:
        """Récupérer les séjours avec filtres multiples pour l'impression"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = '''
            SELECT r.*, 
                   e.nom_etablissement,
                   e.ville as etablissement_ville,
                   p.nom as contact_nom, 
                   p.prenom as contact_prenom,
                   p.email as contact_email,
                   p.telephone as contact_telephone
            FROM reservations r
            LEFT JOIN etablissements e ON r.etablissement_id = e.id
            LEFT JOIN personnes p ON r.id = p.reservation_id AND p.est_contact_principal = TRUE
            WHERE 1=1
        '''
        params = []
        
        # Filtres
        if filters.get('etablissement_id'):
            query += ' AND r.etablissement_id = %s'
            params.append(filters['etablissement_id'])
        
        if filters.get('statut'):
            query += ' AND r.statut = %s'
            params.append(filters['statut'])
        
        if filters.get('date_debut'):
            query += ' AND r.date_arrivee >= %s'
            params.append(filters['date_debut'])
        
        if filters.get('date_fin'):
            query += ' AND r.date_depart <= %s'
            params.append(filters['date_fin'])
        
        if filters.get('numero_reservation'):
            query += ' AND r.numero_reservation ILIKE %s'
            params.append(f'%{filters["numero_reservation"]}%')
        
        query += ' ORDER BY r.date_arrivee DESC'
        
        cur.execute(query, tuple(params))
        sejours = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return serialize_rows(sejours)
