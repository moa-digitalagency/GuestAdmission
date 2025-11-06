#!/usr/bin/env python3
"""
Script pour créer des données de démonstration complètes
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL n'est pas défini")
        sys.exit(1)
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def create_demo_data():
    print("🚀 Création des données de démonstration...\n")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Créer des comptes tenants
        print("👥 Création des comptes tenants...")
        tenants_data = [
            {'nom': 'Groupe Hôtelier Atlas', 'notes': 'Chaîne d\'hôtels de luxe'},
            {'nom': 'Riads & Maisons d\'Hôtes du Maroc', 'notes': 'Réseau de riads authentiques'},
            {'nom': 'Hospitality Partners', 'notes': 'Gestion de plusieurs établissements'}
        ]
        
        tenant_ids = []
        for tenant in tenants_data:
            cur.execute('''
                INSERT INTO tenant_accounts (nom_compte, notes, actif)
                VALUES (%s, %s, TRUE)
                RETURNING id
            ''', (tenant['nom'], tenant['notes']))
            tenant_id = cur.fetchone()['id']
            tenant_ids.append(tenant_id)
            print(f"  ✅ {tenant['nom']}")
        
        # 2. Créer des établissements
        print("\n🏨 Création des établissements...")
        etablissements_data = [
            {
                'tenant': 0,
                'nom': 'Riad Marrakech Excellence',
                'numero': 'ICE001234567',
                'pays': 'Morocco',
                'ville': 'Marrakech',
                'adresse': '45 Derb Sidi Ahmed Soussi, Medina',
                'telephone': '+212 524 123 456',
                'whatsapp': '+212 661 234 567',
                'email': 'contact@riadmarrakech.com',
                'devise': 'MAD',
                'taxe': 2.5,
                'tva': 20.0,
                'charge': 15.0,
                'mode': 'CHAMBRE'
            },
            {
                'tenant': 0,
                'nom': 'Hotel Casablanca Premium',
                'numero': 'ICE007654321',
                'pays': 'Morocco',
                'ville': 'Casablanca',
                'adresse': '123 Boulevard Ain Diab',
                'telephone': '+212 522 987 654',
                'whatsapp': '+212 662 345 678',
                'email': 'info@casablancahotel.ma',
                'devise': 'MAD',
                'taxe': 2.5,
                'tva': 20.0,
                'charge': 12.0,
                'mode': 'CHAMBRE'
            },
            {
                'tenant': 1,
                'nom': 'Riad Essaouira Charm',
                'numero': 'ICE009876543',
                'pays': 'Morocco',
                'ville': 'Essaouira',
                'adresse': '78 Rue de la Skala',
                'telephone': '+212 524 555 777',
                'whatsapp': '+212 663 456 789',
                'email': 'hello@essaouirariad.com',
                'devise': 'MAD',
                'taxe': 2.5,
                'tva': 20.0,
                'charge': 10.0,
                'mode': 'CHAMBRE'
            },
            {
                'tenant': 1,
                'nom': 'Dar Fes Authentique',
                'numero': 'ICE005432167',
                'pays': 'Morocco',
                'ville': 'Fes',
                'adresse': '12 Derb Talaa Kebira, Fes El Bali',
                'telephone': '+212 535 111 222',
                'whatsapp': '+212 664 567 890',
                'email': 'contact@darfes.ma',
                'devise': 'MAD',
                'taxe': 2.5,
                'tva': 20.0,
                'charge': 13.0,
                'mode': 'CHAMBRE'
            },
            {
                'tenant': 2,
                'nom': 'Villa Agadir Ocean View',
                'numero': 'ICE003216549',
                'pays': 'Morocco',
                'ville': 'Agadir',
                'adresse': 'Boulevard du 20 Août',
                'telephone': '+212 528 333 444',
                'whatsapp': '+212 665 678 901',
                'email': 'info@villaagadir.com',
                'devise': 'MAD',
                'taxe': 2.5,
                'tva': 20.0,
                'charge': 11.0,
                'mode': 'CHAMBRE'
            }
        ]
        
        etablissement_ids = []
        for etab in etablissements_data:
            cur.execute('''
                INSERT INTO etablissements (
                    tenant_account_id, nom_etablissement, numero_identification,
                    pays, ville, adresse, telephone, whatsapp, email,
                    devise, taux_taxe_sejour, taux_tva, taux_charge_plateforme,
                    mode_tarification, actif
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id
            ''', (
                tenant_ids[etab['tenant']], etab['nom'], etab['numero'],
                etab['pays'], etab['ville'], etab['adresse'],
                etab['telephone'], etab['whatsapp'], etab['email'],
                etab['devise'], etab['taxe'], etab['tva'], etab['charge'],
                etab['mode']
            ))
            etab_id = cur.fetchone()['id']
            etablissement_ids.append(etab_id)
            print(f"  ✅ {etab['nom']}")
        
        # 3. Créer des utilisateurs admin pour chaque tenant
        print("\n👤 Création des utilisateurs admin...")
        user_ids = []
        for i, tenant_id in enumerate(tenant_ids):
            username = f"admin{i+1}"
            password_hash = generate_password_hash('demo123')
            
            cur.execute('''
                INSERT INTO users (username, password_hash, nom, prenom, email, role)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (username, password_hash, f'Admin', f'Tenant{i+1}', f'admin{i+1}@demo.com', 'ADMIN'))
            user_id = cur.fetchone()['id']
            user_ids.append(user_id)
            
            # Lier l'utilisateur au tenant
            cur.execute('''
                UPDATE tenant_accounts SET primary_admin_user_id = %s WHERE id = %s
            ''', (user_id, tenant_id))
            
            print(f"  ✅ {username} / demo123")
        
        # 4. Créer des chambres
        print("\n🛏️  Création des chambres...")
        types_chambres = [
            ('Standard Simple', 'Standard', 1, 350),
            ('Standard Double', 'Standard', 2, 500),
            ('Deluxe', 'Deluxe', 2, 750),
            ('Suite Junior', 'Suite', 3, 1000),
            ('Suite Familiale', 'Familiale', 4, 1400),
            ('Suite Royale', 'Suite', 2, 1800)
        ]
        
        total_chambres = 0
        chambre_ids_by_etab = {}
        
        for etab_id in etablissement_ids:
            chambre_ids_by_etab[etab_id] = []
            num_chambres = random.randint(4, 6)
            
            for i in range(num_chambres):
                type_info = random.choice(types_chambres)
                nom, type_ch, capacite, prix_base = type_info
                prix = prix_base + random.randint(-100, 200)
                
                cur.execute('''
                    INSERT INTO chambres (
                        etablissement_id, nom, type_chambre, capacite,
                        prix_par_nuit, statut
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (etab_id, f'Chambre {101+i}', type_ch, capacite, prix, 'disponible'))
                
                chambre_id = cur.fetchone()['id']
                chambre_ids_by_etab[etab_id].append(chambre_id)
                total_chambres += 1
        
        print(f"  ✅ {total_chambres} chambres créées")
        
        # 5. Créer des réservations et clients
        print("\n📅 Création des réservations et clients...")
        
        noms = ['Alami', 'Benali', 'Cohen', 'Dubois', 'Garcia', 'Hassan', 'Ibrahim', 
                'Johnson', 'Khan', 'Lopez', 'Martin', 'Nguyen', 'Patel', 'Rodriguez', 'Smith']
        prenoms = ['Ahmed', 'Fatima', 'Mohammed', 'Sarah', 'Youssef', 'Leila', 'Omar', 
                   'Amina', 'Karim', 'Nadia', 'Ali', 'Sophia', 'Lucas', 'Emma', 'Noah']
        pays_liste = ['Morocco', 'France', 'Spain', 'United Kingdom', 'United States', 
                      'Germany', 'Italy', 'Belgium', 'Canada', 'Netherlands']
        
        total_sejours = 0
        total_clients = 0
        
        for etab_id in etablissement_ids:
            chambres = chambre_ids_by_etab[etab_id]
            num_sejours = random.randint(8, 15)
            
            for i in range(num_sejours):
                # Dates variées (passées, en cours, futures)
                jours_offset = random.randint(-30, 60)
                date_arrivee = datetime.now() + timedelta(days=jours_offset)
                nombre_jours = random.randint(2, 10)
                date_depart = date_arrivee + timedelta(days=nombre_jours)
                
                # Numéro unique
                numero_res = f"RES-{date_arrivee.strftime('%Y%m%d')}-{etab_id}{i:03d}"
                
                # Statut basé sur les dates
                if date_depart.date() < datetime.now().date():
                    statut = 'terminee'
                elif date_arrivee.date() > datetime.now().date():
                    statut = 'confirmee'
                else:
                    statut = 'active'
                
                cur.execute('''
                    INSERT INTO reservations (
                        etablissement_id, numero_reservation, date_arrivee, date_depart,
                        nombre_jours, statut
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (etab_id, numero_res, date_arrivee.date(), date_depart.date(), 
                      nombre_jours, statut))
                
                reservation_id = cur.fetchone()['id']
                total_sejours += 1
                
                # Assigner des chambres
                nb_chambres = random.randint(1, min(2, len(chambres)))
                chambres_selectionnees = random.sample(chambres, nb_chambres)
                
                for chambre_id in chambres_selectionnees:
                    cur.execute('''
                        INSERT INTO reservations_chambres (reservation_id, chambre_id)
                        VALUES (%s, %s)
                    ''', (reservation_id, chambre_id))
                
                # Créer des clients
                nb_personnes = random.randint(1, 4)
                for j in range(nb_personnes):
                    nom = random.choice(noms)
                    prenom = random.choice(prenoms)
                    pays_client = random.choice(pays_liste)
                    
                    cur.execute('''
                        INSERT INTO personnes (
                            reservation_id, chambre_id, est_contact_principal,
                            nom, prenom, email, telephone, pays, ville,
                            type_piece_identite, numero_piece_identite
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        reservation_id, chambres_selectionnees[0], j == 0,
                        nom, prenom,
                        f"{prenom.lower()}.{nom.lower()}@email.com",
                        f"+{random.randint(1, 999)} {random.randint(600, 799)} {random.randint(100, 999)} {random.randint(100, 999)}",
                        pays_client, random.choice(['Paris', 'Madrid', 'London', 'New York', 'Berlin']),
                        random.choice(['Passeport', 'CIN', 'CNI', 'ID Card']),
                        f"{'PP' if random.random() > 0.5 else 'ID'}{random.randint(100000, 999999)}"
                    ))
                    total_clients += 1
        
        print(f"  ✅ {total_sejours} réservations créées")
        print(f"  ✅ {total_clients} clients créés")
        
        # 6. Créer des extras
        print("\n🍽️  Création des extras...")
        extras_data = [
            ('Petit-déjeuner', 'Petit-déjeuner continental', 50, 'personne'),
            ('Dîner', 'Dîner 3 plats', 150, 'personne'),
            ('Transfert aéroport', 'Transfert aller simple', 200, 'trajet'),
            ('Excursion désert', 'Excursion guidée', 500, 'personne'),
            ('Spa & Hammam', 'Séance bien-être', 300, 'séance'),
            ('Location vélo', 'Vélo par jour', 80, 'jour')
        ]
        
        total_extras = 0
        for etab_id in etablissement_ids:
            for nom, desc, prix, unite in random.sample(extras_data, random.randint(3, 5)):
                cur.execute('''
                    INSERT INTO extras (etablissement_id, nom, description, prix_unitaire, unite, actif)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                ''', (etab_id, nom, desc, prix, unite))
                total_extras += 1
        
        print(f"  ✅ {total_extras} extras créés")
        
        conn.commit()
        
        print("\n" + "="*50)
        print("✅ DONNÉES DE DÉMONSTRATION CRÉÉES AVEC SUCCÈS!")
        print("="*50)
        print(f"\n📊 Résumé:")
        print(f"   • Comptes tenants: {len(tenant_ids)}")
        print(f"   • Établissements: {len(etablissement_ids)}")
        print(f"   • Chambres: {total_chambres}")
        print(f"   • Réservations: {total_sejours}")
        print(f"   • Clients: {total_clients}")
        print(f"   • Extras: {total_extras}")
        
        print(f"\n🔐 Identifiants de connexion:")
        print(f"   • Platform Admin: admin / admin123")
        for i in range(len(tenant_ids)):
            print(f"   • Tenant Admin {i+1}: admin{i+1} / demo123")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    create_demo_data()
