"""
Service pour les statistiques avancées avec support multi-tenant
"""
from typing import Dict, List, Optional
from ..config.database import get_db_connection
from ..utils.tenant_context import get_accessible_etablissement_ids
from datetime import datetime, timedelta


class StatisticsService:
    """Service pour générer des statistiques détaillées avec filtrage tenant"""
    
    @staticmethod
    def get_global_statistics(tenant_filter: bool = True) -> Dict:
        """
        Récupérer les statistiques globales
        tenant_filter: Si True, filtre par établissements accessibles
        """
        conn = get_db_connection()
        cur = conn.cursor()
        
        if tenant_filter:
            etablissement_ids = get_accessible_etablissement_ids()
            if etablissement_ids is None:  # PLATFORM_ADMIN
                # Pas de filtre
                pass
            elif etablissement_ids:
                placeholders = ','.join(['%s'] * len(etablissement_ids))
                where_clause = f'WHERE etablissement_id IN ({placeholders})'
                params = tuple(etablissement_ids)
            else:
                # Pas d'accès
                return {
                    'total_sejours': 0,
                    'total_clients': 0,
                    'total_etablissements': 0,
                    'total_chambres': 0
                }
        
        if tenant_filter and etablissement_ids and etablissement_ids is not None:
            cur.execute(f'SELECT COUNT(*) as total FROM reservations {where_clause}', params)
            total_sejours = cur.fetchone()['total']
            
            cur.execute(f'''
                SELECT COUNT(DISTINCT p.id) as total FROM personnes p
                INNER JOIN reservations r ON p.reservation_id = r.id
                {where_clause}
            ''', params)
            total_clients = cur.fetchone()['total']
            
            cur.execute(f'SELECT COUNT(*) as total FROM etablissements WHERE actif = TRUE AND id IN ({placeholders})', params)
            total_etablissements = cur.fetchone()['total']
            
            cur.execute(f'SELECT COUNT(*) as total FROM chambres {where_clause}', params)
            total_chambres = cur.fetchone()['total']
        else:
            cur.execute('SELECT COUNT(*) as total FROM reservations')
            total_sejours = cur.fetchone()['total']
            
            cur.execute('SELECT COUNT(DISTINCT id) as total FROM personnes')
            total_clients = cur.fetchone()['total']
            
            cur.execute('SELECT COUNT(*) as total FROM etablissements WHERE actif = TRUE')
            total_etablissements = cur.fetchone()['total']
            
            cur.execute('SELECT COUNT(*) as total FROM chambres')
            total_chambres = cur.fetchone()['total']
        
        cur.close()
        conn.close()
        
        return {
            'total_sejours': total_sejours,
            'total_clients': total_clients,
            'total_etablissements': total_etablissements,
            'total_chambres': total_chambres
        }
    
    @staticmethod
    def get_occupancy_rate(etablissement_id: Optional[int] = None, 
                          date_debut: Optional[str] = None,
                          date_fin: Optional[str] = None) -> Dict:
        """Calculer le taux d'occupation avec filtrage tenant"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            if not date_debut:
                date_debut = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not date_fin:
                date_fin = datetime.now().strftime('%Y-%m-%d')
            
            # Filtrer par établissements accessibles
            etablissement_ids = get_accessible_etablissement_ids()
            
            if etablissement_id:
                # Vérifier l'accès
                if etablissement_ids is not None and etablissement_ids and etablissement_id not in etablissement_ids:
                    return {
                        'total_chambres': 0,
                        'chambres_occupees': 0,
                        'total_nuits': 0,
                        'taux_occupation': 0,
                        'date_debut': date_debut,
                        'date_fin': date_fin,
                        'error': 'Accès refusé'
                    }
                
                cur.execute('''
                    SELECT COUNT(DISTINCT c.id) as total_chambres
                    FROM chambres c
                    WHERE c.etablissement_id = %s
                ''', (etablissement_id,))
                total_chambres = cur.fetchone()['total_chambres'] or 0
                
                cur.execute('''
                    SELECT COUNT(DISTINCT rc.chambre_id) as chambres_occupees,
                           SUM(EXTRACT(DAY FROM (r.date_depart - r.date_arrivee))) as total_nuits
                    FROM reservations_chambres rc
                    JOIN reservations r ON rc.reservation_id = r.id
                    JOIN chambres c ON rc.chambre_id = c.id
                    WHERE c.etablissement_id = %s
                    AND r.date_arrivee >= %s AND r.date_depart <= %s
                    AND r.statut != 'cancelled'
                ''', (etablissement_id, date_debut, date_fin))
                result = cur.fetchone()
            elif etablissement_ids is None:  # PLATFORM_ADMIN
                cur.execute('SELECT COUNT(*) as total_chambres FROM chambres')
                total_chambres = cur.fetchone()['total_chambres'] or 0
                
                cur.execute('''
                    SELECT COUNT(DISTINCT rc.chambre_id) as chambres_occupees,
                           SUM(EXTRACT(DAY FROM (r.date_depart - r.date_arrivee))) as total_nuits
                    FROM reservations_chambres rc
                    JOIN reservations r ON rc.reservation_id = r.id
                    WHERE r.date_arrivee >= %s AND r.date_depart <= %s
                    AND r.statut != 'cancelled'
                ''', (date_debut, date_fin))
                result = cur.fetchone()
            elif etablissement_ids:
                placeholders = ','.join(['%s'] * len(etablissement_ids))
                cur.execute(f'SELECT COUNT(*) as total_chambres FROM chambres WHERE etablissement_id IN ({placeholders})', tuple(etablissement_ids))
                total_chambres = cur.fetchone()['total_chambres'] or 0
                
                cur.execute(f'''
                    SELECT COUNT(DISTINCT rc.chambre_id) as chambres_occupees,
                           SUM(EXTRACT(DAY FROM (r.date_depart - r.date_arrivee))) as total_nuits
                    FROM reservations_chambres rc
                    JOIN reservations r ON rc.reservation_id = r.id
                    WHERE r.etablissement_id IN ({placeholders})
                    AND r.date_arrivee >= %s AND r.date_depart <= %s
                    AND r.statut != 'cancelled'
                ''', tuple(etablissement_ids) + (date_debut, date_fin))
                result = cur.fetchone()
            else:
                return {
                    'total_chambres': 0,
                    'chambres_occupees': 0,
                    'total_nuits': 0,
                    'taux_occupation': 0,
                    'date_debut': date_debut,
                    'date_fin': date_fin
                }
            
            if total_chambres > 0:
                chambres_occupees = result['chambres_occupees'] or 0
                total_nuits = float(result['total_nuits'] or 0)
                
                date_range = (datetime.strptime(date_fin, '%Y-%m-%d') - 
                             datetime.strptime(date_debut, '%Y-%m-%d')).days
                if date_range == 0:
                    date_range = 1
                
                max_nuits_possible = total_chambres * date_range
                taux_occupation = (total_nuits / max_nuits_possible * 100) if max_nuits_possible > 0 else 0
                
                return {
                    'total_chambres': total_chambres,
                    'chambres_occupees': chambres_occupees,
                    'total_nuits': int(total_nuits),
                    'taux_occupation': round(taux_occupation, 2),
                    'date_debut': date_debut,
                    'date_fin': date_fin
                }
            
            return {
                'total_chambres': 0,
                'chambres_occupees': 0,
                'total_nuits': 0,
                'taux_occupation': 0,
                'date_debut': date_debut,
                'date_fin': date_fin
            }
        except Exception as e:
            print(f"Erreur lors du calcul du taux d'occupation: {e}")
            return {
                'total_chambres': 0,
                'chambres_occupees': 0,
                'total_nuits': 0,
                'taux_occupation': 0,
                'date_debut': date_debut or '',
                'date_fin': date_fin or ''
            }
        finally:
            if conn:
                try:
                    cur.close()
                    conn.close()
                except:
                    pass
    
    @staticmethod
    def get_top_countries(etablissement_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Récupérer les pays d'origine les plus fréquents avec filtrage tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Filtrer par établissements accessibles
        etablissement_ids = get_accessible_etablissement_ids()
        
        if etablissement_id:
            # Vérifier l'accès
            if etablissement_ids is not None and etablissement_ids and etablissement_id not in etablissement_ids:
                return []
            
            cur.execute('''
                SELECT p.pays, COUNT(*) as nombre_visiteurs,
                       COUNT(DISTINCT p.reservation_id) as nombre_sejours
                FROM personnes p
                JOIN reservations r ON p.reservation_id = r.id
                WHERE r.etablissement_id = %s AND p.pays IS NOT NULL AND p.pays != ''
                GROUP BY p.pays
                ORDER BY nombre_visiteurs DESC
                LIMIT %s
            ''', (etablissement_id, limit))
        elif etablissement_ids is None:  # PLATFORM_ADMIN
            cur.execute('''
                SELECT p.pays, COUNT(*) as nombre_visiteurs,
                       COUNT(DISTINCT p.reservation_id) as nombre_sejours
                FROM personnes p
                WHERE p.pays IS NOT NULL AND p.pays != ''
                GROUP BY p.pays
                ORDER BY nombre_visiteurs DESC
                LIMIT %s
            ''', (limit,))
        elif etablissement_ids:
            placeholders = ','.join(['%s'] * len(etablissement_ids))
            cur.execute(f'''
                SELECT p.pays, COUNT(*) as nombre_visiteurs,
                       COUNT(DISTINCT p.reservation_id) as nombre_sejours
                FROM personnes p
                JOIN reservations r ON p.reservation_id = r.id
                WHERE r.etablissement_id IN ({placeholders}) AND p.pays IS NOT NULL AND p.pays != ''
                GROUP BY p.pays
                ORDER BY nombre_visiteurs DESC
                LIMIT %s
            ''', tuple(etablissement_ids) + (limit,))
        else:
            return []
        
        countries = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(c) for c in countries] if countries else []
    
    @staticmethod
    def get_sejours_by_occupants(etablissement_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Récupérer les séjours avec le plus grand nombre d'occupants avec filtrage tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Filtrer par établissements accessibles
        etablissement_ids = get_accessible_etablissement_ids()
        
        if etablissement_id:
            # Vérifier l'accès
            if etablissement_ids is not None and etablissement_ids and etablissement_id not in etablissement_ids:
                return []
            
            cur.execute('''
                SELECT r.id, r.numero_reservation, r.date_arrivee, r.date_depart,
                       COUNT(p.id) as nombre_occupants,
                       e.nom_etablissement
                FROM reservations r
                LEFT JOIN personnes p ON r.id = p.reservation_id
                JOIN etablissements e ON r.etablissement_id = e.id
                WHERE r.etablissement_id = %s
                GROUP BY r.id, r.numero_reservation, r.date_arrivee, r.date_depart, e.nom_etablissement
                ORDER BY nombre_occupants DESC
                LIMIT %s
            ''', (etablissement_id, limit))
        elif etablissement_ids is None:  # PLATFORM_ADMIN
            cur.execute('''
                SELECT r.id, r.numero_reservation, r.date_arrivee, r.date_depart,
                       COUNT(p.id) as nombre_occupants,
                       e.nom_etablissement
                FROM reservations r
                LEFT JOIN personnes p ON r.id = p.reservation_id
                JOIN etablissements e ON r.etablissement_id = e.id
                GROUP BY r.id, r.numero_reservation, r.date_arrivee, r.date_depart, e.nom_etablissement
                ORDER BY nombre_occupants DESC
                LIMIT %s
            ''', (limit,))
        elif etablissement_ids:
            placeholders = ','.join(['%s'] * len(etablissement_ids))
            cur.execute(f'''
                SELECT r.id, r.numero_reservation, r.date_arrivee, r.date_depart,
                       COUNT(p.id) as nombre_occupants,
                       e.nom_etablissement
                FROM reservations r
                LEFT JOIN personnes p ON r.id = p.reservation_id
                JOIN etablissements e ON r.etablissement_id = e.id
                WHERE r.etablissement_id IN ({placeholders})
                GROUP BY r.id, r.numero_reservation, r.date_arrivee, r.date_depart, e.nom_etablissement
                ORDER BY nombre_occupants DESC
                LIMIT %s
            ''', tuple(etablissement_ids) + (limit,))
        else:
            return []
        
        sejours = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(s) for s in sejours] if sejours else []
    
    @staticmethod
    def get_sejours_by_rooms(etablissement_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Récupérer les séjours avec le plus de chambres avec filtrage tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Filtrer par établissements accessibles
        etablissement_ids = get_accessible_etablissement_ids()
        
        if etablissement_id:
            # Vérifier l'accès
            if etablissement_ids is not None and etablissement_ids and etablissement_id not in etablissement_ids:
                return []
            
            cur.execute('''
                SELECT r.id, r.numero_reservation, r.date_arrivee, r.date_depart,
                       COUNT(rc.chambre_id) as nombre_chambres,
                       e.nom_etablissement
                FROM reservations r
                LEFT JOIN reservations_chambres rc ON r.id = rc.reservation_id
                JOIN etablissements e ON r.etablissement_id = e.id
                WHERE r.etablissement_id = %s
                GROUP BY r.id, r.numero_reservation, r.date_arrivee, r.date_depart, e.nom_etablissement
                ORDER BY nombre_chambres DESC
                LIMIT %s
            ''', (etablissement_id, limit))
        elif etablissement_ids is None:  # PLATFORM_ADMIN
            cur.execute('''
                SELECT r.id, r.numero_reservation, r.date_arrivee, r.date_depart,
                       COUNT(rc.chambre_id) as nombre_chambres,
                       e.nom_etablissement
                FROM reservations r
                LEFT JOIN reservations_chambres rc ON r.id = rc.reservation_id
                JOIN etablissements e ON r.etablissement_id = e.id
                GROUP BY r.id, r.numero_reservation, r.date_arrivee, r.date_depart, e.nom_etablissement
                ORDER BY nombre_chambres DESC
                LIMIT %s
            ''', (limit,))
        elif etablissement_ids:
            placeholders = ','.join(['%s'] * len(etablissement_ids))
            cur.execute(f'''
                SELECT r.id, r.numero_reservation, r.date_arrivee, r.date_depart,
                       COUNT(rc.chambre_id) as nombre_chambres,
                       e.nom_etablissement
                FROM reservations r
                LEFT JOIN reservations_chambres rc ON r.id = rc.reservation_id
                JOIN etablissements e ON r.etablissement_id = e.id
                WHERE r.etablissement_id IN ({placeholders})
                GROUP BY r.id, r.numero_reservation, r.date_arrivee, r.date_depart, e.nom_etablissement
                ORDER BY nombre_chambres DESC
                LIMIT %s
            ''', tuple(etablissement_ids) + (limit,))
        else:
            return []
        
        sejours = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(s) for s in sejours] if sejours else []
    
    @staticmethod
    def get_revenue_statistics(etablissement_id: Optional[int] = None,
                               date_debut: Optional[str] = None,
                               date_fin: Optional[str] = None) -> Dict:
        """Récupérer les statistiques de revenus avec filtrage tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        if not date_debut:
            date_debut = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not date_fin:
            date_fin = datetime.now().strftime('%Y-%m-%d')
        
        # Filtrer par établissements accessibles
        etablissement_ids = get_accessible_etablissement_ids()
        
        if etablissement_id:
            # Vérifier l'accès
            if etablissement_ids is not None and etablissement_ids and etablissement_id not in etablissement_ids:
                return {
                    'total_hebergement': 0,
                    'total_extras': 0,
                    'total_charges': 0,
                    'total_taxes': 0,
                    'total_revenu': 0,
                    'date_debut': date_debut,
                    'date_fin': date_fin,
                    'error': 'Accès refusé'
                }
            
            cur.execute('''
                SELECT 
                    SUM(facture_hebergement) as total_hebergement,
                    SUM(charge_plateforme) as total_charges,
                    SUM(taxe_sejour) as total_taxes
                FROM reservations
                WHERE etablissement_id = %s
                AND date_arrivee >= %s AND date_depart <= %s
                AND statut != 'cancelled'
            ''', (etablissement_id, date_debut, date_fin))
            
            result = cur.fetchone()
            
            cur.execute('''
                SELECT SUM(se.montant_total) as total_extras
                FROM sejours_extras se
                JOIN reservations r ON se.reservation_id = r.id
                WHERE r.etablissement_id = %s
                AND r.date_arrivee >= %s AND r.date_depart <= %s
            ''', (etablissement_id, date_debut, date_fin))
            
            extras_result = cur.fetchone()
        elif etablissement_ids is None:  # PLATFORM_ADMIN
            cur.execute('''
                SELECT 
                    SUM(facture_hebergement) as total_hebergement,
                    SUM(charge_plateforme) as total_charges,
                    SUM(taxe_sejour) as total_taxes
                FROM reservations
                WHERE date_arrivee >= %s AND date_depart <= %s
                AND statut != 'cancelled'
            ''', (date_debut, date_fin))
            
            result = cur.fetchone()
            
            cur.execute('''
                SELECT SUM(se.montant_total) as total_extras
                FROM sejours_extras se
                JOIN reservations r ON se.reservation_id = r.id
                WHERE r.date_arrivee >= %s AND r.date_depart <= %s
            ''', (date_debut, date_fin))
            
            extras_result = cur.fetchone()
        elif etablissement_ids:
            placeholders = ','.join(['%s'] * len(etablissement_ids))
            cur.execute(f'''
                SELECT 
                    SUM(facture_hebergement) as total_hebergement,
                    SUM(charge_plateforme) as total_charges,
                    SUM(taxe_sejour) as total_taxes
                FROM reservations
                WHERE etablissement_id IN ({placeholders})
                AND date_arrivee >= %s AND date_depart <= %s
                AND statut != 'cancelled'
            ''', tuple(etablissement_ids) + (date_debut, date_fin))
            
            result = cur.fetchone()
            
            cur.execute(f'''
                SELECT SUM(se.montant_total) as total_extras
                FROM sejours_extras se
                JOIN reservations r ON se.reservation_id = r.id
                WHERE r.etablissement_id IN ({placeholders})
                AND r.date_arrivee >= %s AND r.date_depart <= %s
            ''', tuple(etablissement_ids) + (date_debut, date_fin))
            
            extras_result = cur.fetchone()
        else:
            return {
                'total_hebergement': 0,
                'total_extras': 0,
                'total_charges': 0,
                'total_taxes': 0,
                'total_revenu': 0,
                'date_debut': date_debut,
                'date_fin': date_fin
            }
        
        cur.close()
        conn.close()
        
        total_hebergement = float(result['total_hebergement'] or 0)
        total_charges = float(result['total_charges'] or 0)
        total_taxes = float(result['total_taxes'] or 0)
        total_extras = float(extras_result['total_extras'] or 0)
        
        total_revenu = total_hebergement + total_charges + total_taxes + total_extras
        
        return {
            'total_hebergement': total_hebergement,
            'total_extras': total_extras,
            'total_charges': total_charges,
            'total_taxes': total_taxes,
            'total_revenu': total_revenu,
            'date_debut': date_debut,
            'date_fin': date_fin
        }
    
    @staticmethod
    def get_monthly_trends(etablissement_id: Optional[int] = None, months: int = 12) -> List[Dict]:
        """Récupérer les tendances mensuelles avec filtrage tenant"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Filtrer par établissements accessibles
        etablissement_ids = get_accessible_etablissement_ids()
        
        if etablissement_id:
            # Vérifier l'accès
            if etablissement_ids is not None and etablissement_ids and etablissement_id not in etablissement_ids:
                return []
            
            cur.execute('''
                SELECT 
                    TO_CHAR(date_arrivee, 'YYYY-MM') as mois,
                    COUNT(*) as nombre_sejours,
                    SUM(facture_hebergement) as revenu
                FROM reservations
                WHERE etablissement_id = %s
                AND date_arrivee >= CURRENT_DATE - INTERVAL '%s months'
                AND statut != 'cancelled'
                GROUP BY TO_CHAR(date_arrivee, 'YYYY-MM')
                ORDER BY mois DESC
            ''', (etablissement_id, months))
        elif etablissement_ids is None:  # PLATFORM_ADMIN
            cur.execute('''
                SELECT 
                    TO_CHAR(date_arrivee, 'YYYY-MM') as mois,
                    COUNT(*) as nombre_sejours,
                    SUM(facture_hebergement) as revenu
                FROM reservations
                WHERE date_arrivee >= CURRENT_DATE - INTERVAL '%s months'
                AND statut != 'cancelled'
                GROUP BY TO_CHAR(date_arrivee, 'YYYY-MM')
                ORDER BY mois DESC
            ''', (months,))
        elif etablissement_ids:
            placeholders = ','.join(['%s'] * len(etablissement_ids))
            cur.execute(f'''
                SELECT 
                    TO_CHAR(date_arrivee, 'YYYY-MM') as mois,
                    COUNT(*) as nombre_sejours,
                    SUM(facture_hebergement) as revenu
                FROM reservations
                WHERE etablissement_id IN ({placeholders})
                AND date_arrivee >= CURRENT_DATE - INTERVAL '%s months'
                AND statut != 'cancelled'
                GROUP BY TO_CHAR(date_arrivee, 'YYYY-MM')
                ORDER BY mois DESC
            ''', tuple(etablissement_ids) + (months,))
        else:
            return []
        
        trends = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(t) for t in trends] if trends else []
