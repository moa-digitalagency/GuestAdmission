#!/usr/bin/env python3
"""
Script pour créer deux tenants de démonstration avec des données complètes
Ce script crée:
- 2 comptes tenants (clients)
- Chaque tenant a 1-2 établissements
- Chaque établissement a des chambres
- Chaque tenant a un admin principal
- Quelques utilisateurs additionnels
- Quelques réservations de démonstration
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def get_db_connection():
    """Obtenir une connexion à la base de données"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL n'est pas défini dans les variables d'environnement")
            sys.exit(1)
        
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        sys.exit(1)

def create_demo_tenants():
    """Créer deux tenants de démonstration"""
    print("🎨 Création de deux tenants de démonstration...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Nettoyage complet des données de démonstration pour permettre une réexécution
        print("  🧹 Nettoyage des données de démonstration existantes...")
        
        # Supprimer les utilisateurs de démonstration (cela supprimera aussi les associations en cascade)
        demo_usernames = ['admin', 'riad_admin', 'villa_admin', 'riad_staff']
        for username in demo_usernames:
            if username != 'admin':  # On garde admin car c'est le PLATFORM_ADMIN principal
                cur.execute("DELETE FROM users WHERE username = %s", (username,))
        
        # Supprimer tous les tenants (cascade supprimera les établissements et données associées)
        cur.execute("DELETE FROM tenant_accounts")
        
        conn.commit()
        print("  ✅ Nettoyage terminé")
        
        # TENANT 1: Riad Atlas
        print("\n📦 Création du Tenant 1: Riad Atlas...")
        
        # Créer l'admin principal du tenant 1
        print("  👤 Création de l'admin principal: riad_admin")
        password_hash = generate_password_hash('riad123')
        cur.execute('''
            INSERT INTO users (username, password_hash, nom, prenom, email, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', ('riad_admin', password_hash, 'Alami', 'Hassan', 'hassan@riadaltas.ma', 'admin'))
        riad_admin_id = cur.fetchone()['id']
        
        # Créer le compte tenant 1
        print("  🏢 Création du compte tenant: Riad Atlas")
        cur.execute('''
            INSERT INTO tenant_accounts (nom_compte, primary_admin_user_id, notes)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', ('Riad Atlas', riad_admin_id, 'Chaîne de riads traditionnels au Maroc'))
        tenant1_id = cur.fetchone()['id']
        
        # Créer le premier établissement pour tenant 1
        print("  🏨 Création de l'établissement: Riad Atlas Marrakech")
        cur.execute('''
            INSERT INTO etablissements (
                tenant_account_id, nom_etablissement, numero_identification, 
                pays, ville, adresse, telephone, email, devise,
                taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            tenant1_id, 'Riad Atlas Marrakech', 'RIAD-MRK-001',
            'Maroc', 'Marrakech', '12 Derb Sidi Ahmed, Médina', '+212 524 123456',
            'marrakech@riadaltas.ma', 'MAD', 2.5, 20.0, 15.0, True
        ))
        etab1_id = cur.fetchone()['id']
        
        # Associer l'admin au premier établissement
        print("  🔗 Association de l'admin avec l'établissement")
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role, is_primary_admin)
            VALUES (%s, %s, %s, %s)
        ''', (riad_admin_id, etab1_id, 'admin', True))
        
        # Mettre à jour l'établissement actif de l'admin
        cur.execute('''
            UPDATE users SET etablissement_id = %s WHERE id = %s
        ''', (etab1_id, riad_admin_id))
        
        # Créer des chambres pour le premier établissement
        print("  🛏️  Création de 5 chambres pour Riad Atlas Marrakech")
        chambres_riad1 = [
            ('Chambre Sahara', 'Suite avec vue sur la médina', 2, 800.00, 'disponible'),
            ('Chambre Atlas', 'Chambre double confort', 2, 600.00, 'disponible'),
            ('Suite Royale', 'Suite de luxe avec terrasse privée', 4, 1500.00, 'disponible'),
            ('Chambre Oasis', 'Chambre simple avec patio', 1, 400.00, 'disponible'),
            ('Suite Jardin', 'Suite familiale avec jardin', 3, 1200.00, 'disponible'),
        ]
        
        for nom, description, capacite, prix, statut in chambres_riad1:
            cur.execute('''
                INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab1_id, nom, description, capacite, prix, statut))
        
        # Créer le deuxième établissement pour tenant 1
        print("  🏨 Création de l'établissement: Riad Atlas Fès")
        cur.execute('''
            INSERT INTO etablissements (
                tenant_account_id, nom_etablissement, numero_identification, 
                pays, ville, adresse, telephone, email, devise,
                taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            tenant1_id, 'Riad Atlas Fès', 'RIAD-FES-001',
            'Maroc', 'Fès', '45 Derb Guerniz, Médina', '+212 535 987654',
            'fes@riadaltas.ma', 'MAD', 2.5, 20.0, 15.0, True
        ))
        etab2_id = cur.fetchone()['id']
        
        # Associer l'admin au deuxième établissement
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role)
            VALUES (%s, %s, %s)
        ''', (riad_admin_id, etab2_id, 'admin'))
        
        # Créer des chambres pour le deuxième établissement
        print("  🛏️  Création de 4 chambres pour Riad Atlas Fès")
        chambres_riad2 = [
            ('Chambre Andalouse', 'Chambre traditionnelle andalouse', 2, 700.00, 'disponible'),
            ('Suite Bleue', 'Suite avec décoration bleue de Fès', 2, 900.00, 'disponible'),
            ('Chambre Zellige', 'Chambre avec mosaïques traditionnelles', 2, 650.00, 'disponible'),
            ('Suite Panorama', 'Suite avec vue panoramique', 3, 1100.00, 'disponible'),
        ]
        
        for nom, description, capacite, prix, statut in chambres_riad2:
            cur.execute('''
                INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab2_id, nom, description, capacite, prix, statut))
        
        # Créer un utilisateur supplémentaire pour tenant 1
        print("  👤 Création d'un utilisateur supplémentaire: riad_staff")
        password_hash = generate_password_hash('staff123')
        cur.execute('''
            INSERT INTO users (username, password_hash, nom, prenom, email, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', ('riad_staff', password_hash, 'Bennis', 'Fatima', 'fatima@riadaltas.ma', 'user'))
        riad_staff_id = cur.fetchone()['id']
        
        # Associer le staff aux deux établissements
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role)
            VALUES (%s, %s, %s), (%s, %s, %s)
        ''', (riad_staff_id, etab1_id, 'user', riad_staff_id, etab2_id, 'user'))
        
        # TENANT 2: Villa Ocean
        print("\n📦 Création du Tenant 2: Villa Ocean...")
        
        # Créer l'admin principal du tenant 2
        print("  👤 Création de l'admin principal: villa_admin")
        password_hash = generate_password_hash('villa123')
        cur.execute('''
            INSERT INTO users (username, password_hash, nom, prenom, email, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', ('villa_admin', password_hash, 'Idrissi', 'Karim', 'karim@villaocean.ma', 'admin'))
        villa_admin_id = cur.fetchone()['id']
        
        # Créer le compte tenant 2
        print("  🏢 Création du compte tenant: Villa Ocean")
        cur.execute('''
            INSERT INTO tenant_accounts (nom_compte, primary_admin_user_id, notes)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', ('Villa Ocean', villa_admin_id, 'Villas de luxe en bord de mer'))
        tenant2_id = cur.fetchone()['id']
        
        # Créer l'établissement pour tenant 2
        print("  🏨 Création de l'établissement: Villa Ocean Essaouira")
        cur.execute('''
            INSERT INTO etablissements (
                tenant_account_id, nom_etablissement, numero_identification, 
                pays, ville, adresse, telephone, email, devise,
                taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            tenant2_id, 'Villa Ocean Essaouira', 'VILLA-ESS-001',
            'Maroc', 'Essaouira', 'Boulevard Mohammed V, Plage', '+212 524 789012',
            'essaouira@villaocean.ma', 'MAD', 2.5, 20.0, 15.0, True
        ))
        etab3_id = cur.fetchone()['id']
        
        # Associer l'admin au troisième établissement
        print("  🔗 Association de l'admin avec l'établissement")
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role, is_primary_admin)
            VALUES (%s, %s, %s, %s)
        ''', (villa_admin_id, etab3_id, 'admin', True))
        
        # Mettre à jour l'établissement actif de l'admin
        cur.execute('''
            UPDATE users SET etablissement_id = %s WHERE id = %s
        ''', (etab3_id, villa_admin_id))
        
        # Créer des chambres pour le troisième établissement
        print("  🛏️  Création de 6 chambres pour Villa Ocean Essaouira")
        chambres_villa = [
            ('Villa Vue Mer 1', 'Villa de luxe avec vue sur l\'océan', 4, 2500.00, 'disponible'),
            ('Villa Vue Mer 2', 'Villa de luxe avec piscine privée', 6, 3500.00, 'disponible'),
            ('Suite Ocean', 'Suite avec terrasse vue mer', 2, 1800.00, 'disponible'),
            ('Chambre Premium', 'Chambre premium avec balcon', 2, 1200.00, 'disponible'),
            ('Bungalow Plage', 'Bungalow direct sur la plage', 3, 2000.00, 'disponible'),
            ('Suite Familiale', 'Suite familiale avec kitchenette', 4, 1600.00, 'disponible'),
        ]
        
        for nom, description, capacite, prix, statut in chambres_villa:
            cur.execute('''
                INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab3_id, nom, description, capacite, prix, statut))
        
        # Créer quelques extras pour chaque établissement
        print("\n🎁 Création des extras pour les établissements...")
        
        # Extras pour Riad Atlas Marrakech
        extras_riad = [
            ('Petit-déjeuner berbère', 'Petit-déjeuner traditionnel', 80.00, 'personne'),
            ('Transfert aéroport', 'Transfert depuis/vers l\'aéroport', 250.00, 'trajet'),
            ('Massage traditionnel', 'Massage au hammam', 400.00, 'séance'),
            ('Cours de cuisine', 'Atelier cuisine marocaine', 500.00, 'séance'),
        ]
        
        for nom, description, prix, unite in extras_riad:
            cur.execute('''
                INSERT INTO extras (etablissement_id, nom, description, prix_unitaire, unite, actif)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab1_id, nom, description, prix, unite, True))
            # Aussi pour Fès
            cur.execute('''
                INSERT INTO extras (etablissement_id, nom, description, prix_unitaire, unite, actif)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab2_id, nom, description, prix, unite, True))
        
        # Extras pour Villa Ocean
        extras_villa = [
            ('Petit-déjeuner continental', 'Petit-déjeuner buffet', 120.00, 'personne'),
            ('Transfert aéroport premium', 'Transfert en Mercedes', 400.00, 'trajet'),
            ('Spa et massage', 'Séance spa complète', 600.00, 'séance'),
            ('Excursion îles Purpuraires', 'Excursion en bateau', 800.00, 'personne'),
            ('Location vélo', 'Location de vélo à la journée', 100.00, 'jour'),
        ]
        
        for nom, description, prix, unite in extras_villa:
            cur.execute('''
                INSERT INTO extras (etablissement_id, nom, description, prix_unitaire, unite, actif)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab3_id, nom, description, prix, unite, True))
        
        # Créer quelques réservations de démonstration
        print("\n📅 Création de réservations de démonstration...")
        
        # Réservations pour Riad Atlas Marrakech
        today = datetime.now().date()
        
        # Récupérer les IDs des chambres
        cur.execute('SELECT id FROM chambres WHERE etablissement_id = %s LIMIT 2', (etab1_id,))
        chambres_mrk = cur.fetchall()
        
        # Réservation 1 pour Riad Marrakech
        date_arrivee = today + timedelta(days=5)
        date_depart = today + timedelta(days=9)
        nombre_jours = (date_depart - date_arrivee).days
        
        cur.execute('''
            INSERT INTO reservations (
                etablissement_id, numero_reservation, date_arrivee, date_depart,
                nombre_jours, facture_hebergement, statut
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            etab1_id, f'MRK-{today.strftime("%Y%m%d")}-001', date_arrivee, date_depart,
            nombre_jours, 800.00 * nombre_jours, 'active'
        ))
        res1_id = cur.fetchone()['id']
        
        # Ajouter une chambre à la réservation
        if chambres_mrk:
            cur.execute('''
                INSERT INTO reservations_chambres (reservation_id, chambre_id)
                VALUES (%s, %s)
            ''', (res1_id, chambres_mrk[0]['id']))
            
            # Ajouter un client
            cur.execute('''
                INSERT INTO personnes (
                    reservation_id, chambre_id, est_contact_principal,
                    nom, prenom, email, telephone, pays, ville
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                res1_id, chambres_mrk[0]['id'], True,
                'Dubois', 'Jean', 'jean.dubois@email.fr', '+33 6 12 34 56 78',
                'France', 'Paris'
            ))
        
        # Valider toutes les modifications
        conn.commit()
        
        print("\n✅ Création des tenants de démonstration terminée avec succès!")
        
        # Afficher un résumé
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DES TENANTS DE DÉMONSTRATION")
        print("="*60)
        
        print("\n🏢 TENANT 1: Riad Atlas")
        print("  👤 Admin: riad_admin / riad123")
        print("  📧 Email: hassan@riadaltas.ma")
        print(f"  🏨 Établissements: 2 (Marrakech, Fès)")
        print(f"  🛏️  Chambres totales: 9")
        print(f"  👥 Utilisateurs: 2 (admin + 1 staff)")
        
        print("\n🏢 TENANT 2: Villa Ocean")
        print("  👤 Admin: villa_admin / villa123")
        print("  📧 Email: karim@villaocean.ma")
        print(f"  🏨 Établissements: 1 (Essaouira)")
        print(f"  🛏️  Chambres totales: 6")
        print(f"  👥 Utilisateurs: 1 (admin)")
        
        print("\n🔑 PLATFORM ADMIN")
        print("  👤 Admin: admin / admin123")
        print("  🎯 Rôle: PLATFORM_ADMIN")
        print("  📍 Dashboard: /platform-admin")
        
        print("\n" + "="*60)
        print("✅ Vous pouvez maintenant vous connecter avec:")
        print("  - admin/admin123 (Platform Admin)")
        print("  - riad_admin/riad123 (Tenant 1 Admin)")
        print("  - villa_admin/villa123 (Tenant 2 Admin)")
        print("="*60 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la création des tenants: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    create_demo_tenants()
