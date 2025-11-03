"""
Service pour la gestion des extras
"""
from typing import List, Dict, Optional
from ..config.database import get_db_connection
from ..utils import serialize_rows, serialize_row


class ExtraService:
    """Service pour gérer les extras (suppléments facturables)"""
    
    @staticmethod
    def create_extra(data: Dict) -> Optional[int]:
        """Créer un nouvel extra"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO extras (
                etablissement_id, nom, description, prix_unitaire, 
                unite_mesure, actif
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            data.get('etablissement_id'),
            data.get('nom'),
            data.get('description', ''),
            data.get('prix_unitaire', 0),
            data.get('unite_mesure', 'unité'),
            data.get('actif', True)
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return result['id'] if result else None
    
    @staticmethod
    def get_all_extras(etablissement_id: Optional[int] = None, actif_only: bool = True) -> List[Dict]:
        """Récupérer tous les extras"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = '''
            SELECT e.*, et.nom_etablissement
            FROM extras e
            LEFT JOIN etablissements et ON e.etablissement_id = et.id
            WHERE 1=1
        '''
        params = []
        
        if actif_only:
            query += ' AND e.actif = TRUE'
        
        if etablissement_id:
            query += ' AND e.etablissement_id = %s'
            params.append(etablissement_id)
        
        query += ' ORDER BY e.nom'
        
        cur.execute(query, tuple(params))
        extras = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return serialize_rows(extras)
    
    @staticmethod
    def get_extra_by_id(extra_id: int) -> Optional[Dict]:
        """Récupérer un extra par son ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM extras WHERE id = %s', (extra_id,))
        extra = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(extra) if extra else None
    
    @staticmethod
    def update_extra(extra_id: int, data: Dict) -> bool:
        """Mettre à jour un extra"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE extras SET
                nom = %s, description = %s, prix_unitaire = %s,
                unite_mesure = %s, actif = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (
            data.get('nom'),
            data.get('description'),
            data.get('prix_unitaire'),
            data.get('unite_mesure'),
            data.get('actif'),
            extra_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
    
    @staticmethod
    def delete_extra(extra_id: int) -> bool:
        """Supprimer un extra"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM extras WHERE id = %s', (extra_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
    
    @staticmethod
    def add_extra_to_sejour(sejour_id: int, extra_id: int, quantite: int) -> Optional[int]:
        """Ajouter un extra à un séjour"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Récupérer le prix de l'extra
        cur.execute('SELECT prix_unitaire FROM extras WHERE id = %s', (extra_id,))
        extra = cur.fetchone()
        
        if not extra:
            cur.close()
            conn.close()
            return None
        
        montant_total = float(extra['prix_unitaire']) * quantite
        
        # Ajouter l'extra au séjour
        cur.execute('''
            INSERT INTO sejours_extras (sejour_id, extra_id, quantite, montant_total)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        ''', (sejour_id, extra_id, quantite, montant_total))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return result['id'] if result else None
    
    @staticmethod
    def get_extras_by_sejour(sejour_id: int) -> List[Dict]:
        """Récupérer les extras d'un séjour"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT e.*, se.quantite, se.montant_total, se.date_ajout, se.id as sejour_extra_id
            FROM extras e
            JOIN sejours_extras se ON e.id = se.extra_id
            WHERE se.sejour_id = %s
            ORDER BY se.date_ajout DESC
        ''', (sejour_id,))
        
        extras = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return serialize_rows(extras)
    
    @staticmethod
    def remove_extra_from_sejour(sejour_extra_id: int) -> bool:
        """Retirer un extra d'un séjour"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('DELETE FROM sejours_extras WHERE id = %s', (sejour_extra_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True
    
    @staticmethod
    def get_extras_summary_by_etablissement(etablissement_id: int, date_debut: Optional[str] = None, date_fin: Optional[str] = None) -> List[Dict]:
        """Récupérer le sommaire des extras par établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = '''
            SELECT 
                e.nom as extra_nom,
                e.unite_mesure,
                e.prix_unitaire,
                COUNT(se.id) as nombre_utilisations,
                SUM(se.quantite) as quantite_totale,
                SUM(se.montant_total) as montant_total
            FROM extras e
            LEFT JOIN sejours_extras se ON e.id = se.extra_id
            LEFT JOIN reservations r ON se.sejour_id = r.id
            WHERE e.etablissement_id = %s
        '''
        params = [etablissement_id]
        
        if date_debut:
            query += ' AND r.date_arrivee >= %s'
            params.append(date_debut)
        
        if date_fin:
            query += ' AND r.date_depart <= %s'
            params.append(date_fin)
        
        query += '''
            GROUP BY e.id, e.nom, e.unite_mesure, e.prix_unitaire
            ORDER BY montant_total DESC NULLS LAST
        '''
        
        cur.execute(query, tuple(params))
        summary = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return serialize_rows(summary)
