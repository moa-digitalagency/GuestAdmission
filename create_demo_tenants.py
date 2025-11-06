#!/usr/bin/env python3
"""
Script pour créer trois tenants de démonstration avec des données complètes
Ce script crée:
- 3 comptes tenants (clients)
- 5 établissements au total (2 pour tenant 1, 2 pour tenant 2, 1 pour tenant 3)
- Chaque établissement a des chambres
- Chaque tenant a un admin principal
- Quelques extras et séjours de démonstration
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
    """Créer trois tenants de démonstration"""
    print("🎨 Création de trois tenants de démonstration...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Nettoyage complet des données de démonstration pour permettre une réexécution
        print("  🧹 Nettoyage des données de démonstration existantes...")
        
        # Supprimer les utilisateurs de démonstration (cela supprimera aussi les associations en cascade)
        demo_usernames = ['admin', 'admin1', 'admin2', 'admin3', 'riad_admin', 'villa_admin', 'riad_staff']
        for username in demo_usernames:
            if username != 'admin':  # On garde admin car c'est le PLATFORM_ADMIN principal
                cur.execute("DELETE FROM users WHERE username = %s", (username,))
        
        # Supprimer tous les tenants (cascade supprimera les établissements et données associées)
        cur.execute("DELETE FROM tenant_accounts")
        
        conn.commit()
        print("  ✅ Nettoyage terminé")
        
        # TENANT 1: Groupe Hôtelier Atlas
        print("\n📦 Création du Tenant 1: Groupe Hôtelier Atlas...")
        
        # Créer l'admin principal du tenant 1
        print("  👤 Création de l'admin principal: admin1")
        password_hash = generate_password_hash('demo123')
        cur.execute('''
            INSERT INTO users (username, password_hash, nom, prenom, email, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', ('admin1', password_hash, 'Atlas', 'Admin', 'admin@groupeatlas.ma', 'admin'))
        admin1_id = cur.fetchone()['id']
        
        # Créer le compte tenant 1
        print("  🏢 Création du compte tenant: Groupe Hôtelier Atlas")
        cur.execute('''
            INSERT INTO tenant_accounts (nom_compte, primary_admin_user_id, notes)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', ('Groupe Hôtelier Atlas', admin1_id, 'Groupe hôtelier professionnel au Maroc'))
        tenant1_id = cur.fetchone()['id']
        
        # Créer le premier établissement pour tenant 1
        print("  🏨 Création de l'établissement: Riad Marrakech Excellence")
        cur.execute('''
            INSERT INTO etablissements (
                tenant_account_id, nom_etablissement, numero_identification, 
                pays, ville, adresse, telephone, email, devise,
                taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            tenant1_id, 'Riad Marrakech Excellence', 'RIAD-MRK-001',
            'Maroc', 'Marrakech', '12 Derb Sidi Ahmed, Médina', '+212 524 123456',
            'marrakech@groupeatlas.ma', 'MAD', 2.5, 20.0, 15.0, True
        ))
        etab1_id = cur.fetchone()['id']
        
        # Associer l'admin au premier établissement
        print("  🔗 Association de l'admin avec l'établissement")
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role, is_primary_admin)
            VALUES (%s, %s, %s, %s)
        ''', (admin1_id, etab1_id, 'admin', True))
        
        # Mettre à jour l'établissement actif de l'admin
        cur.execute('''
            UPDATE users SET etablissement_id = %s WHERE id = %s
        ''', (etab1_id, admin1_id))
        
        # Créer des chambres pour le premier établissement
        print("  🛏️  Création de 5 chambres pour Riad Marrakech Excellence")
        chambres_etab1 = [
            ('Chambre Sahara', 'Suite avec vue sur la médina', 2, 800.00, 'disponible'),
            ('Chambre Atlas', 'Chambre double confort', 2, 600.00, 'disponible'),
            ('Suite Royale', 'Suite de luxe avec terrasse privée', 4, 1500.00, 'disponible'),
            ('Chambre Oasis', 'Chambre simple avec patio', 1, 400.00, 'disponible'),
            ('Suite Jardin', 'Suite familiale avec jardin', 3, 1200.00, 'disponible'),
        ]
        
        for nom, description, capacite, prix, statut in chambres_etab1:
            cur.execute('''
                INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab1_id, nom, description, capacite, prix, statut))
        
        # Créer le deuxième établissement pour tenant 1
        print("  🏨 Création de l'établissement: Hotel Casablanca Premium")
        cur.execute('''
            INSERT INTO etablissements (
                tenant_account_id, nom_etablissement, numero_identification, 
                pays, ville, adresse, telephone, email, devise,
                taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            tenant1_id, 'Hotel Casablanca Premium', 'HOTEL-CASA-001',
            'Maroc', 'Casablanca', 'Boulevard de la Corniche', '+212 522 456789',
            'casablanca@groupeatlas.ma', 'MAD', 2.5, 20.0, 15.0, True
        ))
        etab2_id = cur.fetchone()['id']
        
        # Associer l'admin au deuxième établissement
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role)
            VALUES (%s, %s, %s)
        ''', (admin1_id, etab2_id, 'admin'))
        
        # Créer des chambres pour le deuxième établissement
        print("  🛏️  Création de 4 chambres pour Hotel Casablanca Premium")
        chambres_etab2 = [
            ('Suite Executive', 'Suite business avec vue sur mer', 2, 1200.00, 'disponible'),
            ('Chambre Deluxe', 'Chambre deluxe moderne', 2, 900.00, 'disponible'),
            ('Suite Présidentielle', 'Suite de luxe présidentielle', 4, 2500.00, 'disponible'),
            ('Chambre Superior', 'Chambre superior confort', 2, 750.00, 'disponible'),
        ]
        
        for nom, description, capacite, prix, statut in chambres_etab2:
            cur.execute('''
                INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab2_id, nom, description, capacite, prix, statut))
        
        # TENANT 2: Riads & Maisons d'Hôtes du Maroc
        print("\n📦 Création du Tenant 2: Riads & Maisons d'Hôtes du Maroc...")
        
        # Créer l'admin principal du tenant 2
        print("  👤 Création de l'admin principal: admin2")
        password_hash = generate_password_hash('demo123')
        cur.execute('''
            INSERT INTO users (username, password_hash, nom, prenom, email, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', ('admin2', password_hash, 'Riad', 'Manager', 'admin@riadmaroc.ma', 'admin'))
        admin2_id = cur.fetchone()['id']
        
        # Créer le compte tenant 2
        print("  🏢 Création du compte tenant: Riads & Maisons d'Hôtes du Maroc")
        cur.execute('''
            INSERT INTO tenant_accounts (nom_compte, primary_admin_user_id, notes)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', ('Riads & Maisons d\'Hôtes du Maroc', admin2_id, 'Réseau de riads authentiques'))
        tenant2_id = cur.fetchone()['id']
        
        # Créer le premier établissement pour tenant 2
        print("  🏨 Création de l'établissement: Riad Essaouira Charm")
        cur.execute('''
            INSERT INTO etablissements (
                tenant_account_id, nom_etablissement, numero_identification, 
                pays, ville, adresse, telephone, email, devise,
                taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            tenant2_id, 'Riad Essaouira Charm', 'RIAD-ESS-001',
            'Maroc', 'Essaouira', 'Rue de la Skala, Médina', '+212 524 445566',
            'essaouira@riadmaroc.ma', 'MAD', 2.5, 20.0, 15.0, True
        ))
        etab3_id = cur.fetchone()['id']
        
        # Associer l'admin au troisième établissement
        print("  🔗 Association de l'admin avec l'établissement")
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role, is_primary_admin)
            VALUES (%s, %s, %s, %s)
        ''', (admin2_id, etab3_id, 'admin', True))
        
        # Mettre à jour l'établissement actif de l'admin
        cur.execute('''
            UPDATE users SET etablissement_id = %s WHERE id = %s
        ''', (etab3_id, admin2_id))
        
        # Créer des chambres pour le troisième établissement
        print("  🛏️  Création de 4 chambres pour Riad Essaouira Charm")
        chambres_etab3 = [
            ('Chambre Ocean', 'Chambre avec vue océan', 2, 650.00, 'disponible'),
            ('Suite Médina', 'Suite dans la médina', 2, 800.00, 'disponible'),
            ('Chambre Tradition', 'Chambre traditionnelle', 2, 550.00, 'disponible'),
            ('Suite Romantique', 'Suite romantique avec terrasse', 2, 900.00, 'disponible'),
        ]
        
        for nom, description, capacite, prix, statut in chambres_etab3:
            cur.execute('''
                INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab3_id, nom, description, capacite, prix, statut))
        
        # Créer le deuxième établissement pour tenant 2
        print("  🏨 Création de l'établissement: Dar Fes Authentique")
        cur.execute('''
            INSERT INTO etablissements (
                tenant_account_id, nom_etablissement, numero_identification, 
                pays, ville, adresse, telephone, email, devise,
                taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            tenant2_id, 'Dar Fes Authentique', 'DAR-FES-001',
            'Maroc', 'Fès', 'Derb Zeitoun, Médina', '+212 535 778899',
            'fes@riadmaroc.ma', 'MAD', 2.5, 20.0, 15.0, True
        ))
        etab4_id = cur.fetchone()['id']
        
        # Associer l'admin au quatrième établissement
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role)
            VALUES (%s, %s, %s)
        ''', (admin2_id, etab4_id, 'admin'))
        
        # Créer des chambres pour le quatrième établissement
        print("  🛏️  Création de 3 chambres pour Dar Fes Authentique")
        chambres_etab4 = [
            ('Chambre Bleue de Fès', 'Décor bleu traditionnel de Fès', 2, 700.00, 'disponible'),
            ('Suite Artisanale', 'Suite avec artisanat local', 2, 850.00, 'disponible'),
            ('Chambre Patio', 'Chambre donnant sur le patio', 2, 600.00, 'disponible'),
        ]
        
        for nom, description, capacite, prix, statut in chambres_etab4:
            cur.execute('''
                INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab4_id, nom, description, capacite, prix, statut))
        
        # TENANT 3: Hospitality Partners
        print("\n📦 Création du Tenant 3: Hospitality Partners...")
        
        # Créer l'admin principal du tenant 3
        print("  👤 Création de l'admin principal: admin3")
        password_hash = generate_password_hash('demo123')
        cur.execute('''
            INSERT INTO users (username, password_hash, nom, prenom, email, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', ('admin3', password_hash, 'Hospitality', 'Admin', 'admin@hospitalitypartners.ma', 'admin'))
        admin3_id = cur.fetchone()['id']
        
        # Créer le compte tenant 3
        print("  🏢 Création du compte tenant: Hospitality Partners")
        cur.execute('''
            INSERT INTO tenant_accounts (nom_compte, primary_admin_user_id, notes)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', ('Hospitality Partners', admin3_id, 'Villas de luxe en bord de mer'))
        tenant3_id = cur.fetchone()['id']
        
        # Créer l'établissement pour tenant 3
        print("  🏨 Création de l'établissement: Villa Agadir Ocean View")
        cur.execute('''
            INSERT INTO etablissements (
                tenant_account_id, nom_etablissement, numero_identification, 
                pays, ville, adresse, telephone, email, devise,
                taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            tenant3_id, 'Villa Agadir Ocean View', 'VILLA-AGA-001',
            'Maroc', 'Agadir', 'Boulevard du 20 Août, Front de Mer', '+212 528 334455',
            'agadir@hospitalitypartners.ma', 'MAD', 2.5, 20.0, 15.0, True
        ))
        etab5_id = cur.fetchone()['id']
        
        # Associer l'admin au cinquième établissement
        print("  🔗 Association de l'admin avec l'établissement")
        cur.execute('''
            INSERT INTO user_etablissements (user_id, etablissement_id, role, is_primary_admin)
            VALUES (%s, %s, %s, %s)
        ''', (admin3_id, etab5_id, 'admin', True))
        
        # Mettre à jour l'établissement actif de l'admin
        cur.execute('''
            UPDATE users SET etablissement_id = %s WHERE id = %s
        ''', (etab5_id, admin3_id))
        
        # Créer des chambres pour le cinquième établissement
        print("  🛏️  Création de 5 chambres pour Villa Agadir Ocean View")
        chambres_etab5 = [
            ('Villa Premium 1', 'Villa de luxe avec piscine', 6, 3000.00, 'disponible'),
            ('Villa Premium 2', 'Villa avec vue panoramique', 4, 2500.00, 'disponible'),
            ('Suite Ocean', 'Suite avec terrasse vue mer', 2, 1500.00, 'disponible'),
            ('Appartement Family', 'Appartement familial', 4, 1800.00, 'disponible'),
            ('Bungalow Plage', 'Bungalow direct sur la plage', 3, 2200.00, 'disponible'),
        ]
        
        for nom, description, capacite, prix, statut in chambres_etab5:
            cur.execute('''
                INSERT INTO chambres (etablissement_id, nom, description, capacite, prix_par_nuit, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (etab5_id, nom, description, capacite, prix, statut))
        
        # Créer quelques extras pour les établissements
        print("\n🎁 Création des extras pour les établissements...")
        
        # Extras communs
        extras_communs = [
            ('Petit-déjeuner', 'Petit-déjeuner complet', 80.00, 'personne'),
            ('Transfert aéroport', 'Transfert depuis/vers l\'aéroport', 250.00, 'trajet'),
            ('Spa et massage', 'Séance de relaxation', 400.00, 'séance'),
        ]
        
        # Ajouter extras à tous les établissements
        for etab_id in [etab1_id, etab2_id, etab3_id, etab4_id, etab5_id]:
            for nom, description, prix, unite in extras_communs:
                cur.execute('''
                    INSERT INTO extras (etablissement_id, nom, description, prix_unitaire, unite, actif)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (etab_id, nom, description, prix, unite, True))
        
        # Créer quelques séjours de démonstration
        print("\n📅 Création de séjours de démonstration...")
        
        # Séjours pour Riad Atlas Marrakech
        today = datetime.now().date()
        
        # Récupérer les IDs des chambres
        cur.execute('SELECT id FROM chambres WHERE etablissement_id = %s LIMIT 2', (etab1_id,))
        chambres_mrk = cur.fetchall()
        
        # Séjour 1 pour Riad Marrakech
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
        
        # Ajouter une chambre à la séjour
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
        print("\n" + "="*70)
        print("📊 RÉSUMÉ DES TENANTS DE DÉMONSTRATION")
        print("="*70)
        
        print("\n🏢 TENANT 1: Groupe Hôtelier Atlas")
        print("  👤 Admin: admin1 / demo123")
        print("  📧 Email: admin@groupeatlas.ma")
        print(f"  🏨 Établissements: 2 (Riad Marrakech Excellence, Hotel Casablanca Premium)")
        print(f"  🛏️  Chambres totales: 9")
        
        print("\n🏢 TENANT 2: Riads & Maisons d'Hôtes du Maroc")
        print("  👤 Admin: admin2 / demo123")
        print("  📧 Email: admin@riadmaroc.ma")
        print(f"  🏨 Établissements: 2 (Riad Essaouira Charm, Dar Fes Authentique)")
        print(f"  🛏️  Chambres totales: 7")
        
        print("\n🏢 TENANT 3: Hospitality Partners")
        print("  👤 Admin: admin3 / demo123")
        print("  📧 Email: admin@hospitalitypartners.ma")
        print(f"  🏨 Établissements: 1 (Villa Agadir Ocean View)")
        print(f"  🛏️  Chambres totales: 5")
        
        print("\n🔑 PLATFORM ADMIN")
        print("  👤 Admin: admin / admin123")
        print("  🎯 Rôle: PLATFORM_ADMIN")
        print("  📍 Dashboard: /platform-admin")
        
        print("\n" + "="*70)
        print("✅ Vous pouvez maintenant vous connecter avec:")
        print("  - admin/admin123 (Platform Admin)")
        print("  - admin1/demo123 (Groupe Hôtelier Atlas)")
        print("  - admin2/demo123 (Riads & Maisons d'Hôtes du Maroc)")
        print("  - admin3/demo123 (Hospitality Partners)")
        print("="*70 + "\n")
        
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
