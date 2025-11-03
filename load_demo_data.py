#!/usr/bin/env python3
"""
Script pour charger des données de démonstration dans la base de données
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import random

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

def load_demo_data():
    """Charger les données de démonstration"""
    print("📦 Chargement des données de démonstration...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Vérifier s'il y a déjà des données
        cur.execute("SELECT COUNT(*) as count FROM etablissements WHERE nom_etablissement != 'Maison d''Hôte'")
        result = cur.fetchone()
        if result and result['count'] > 0:
            if len(sys.argv) > 1 and sys.argv[1] == '--force':
                print("\n🗑️ Suppression des anciennes données de démonstration (mode force)...")
            else:
                response = input("\n⚠️ Des données de démonstration existent déjà. Voulez-vous les écraser? (o/n): ")
                if response.lower() != 'o':
                    print("❌ Opération annulée")
                    return
                print("\n🗑️ Suppression des anciennes données de démonstration...")
            
            cur.execute("DELETE FROM reservations_chambres")
            cur.execute("DELETE FROM personnes")
            cur.execute("DELETE FROM reservations")
            cur.execute("DELETE FROM chambres")
            cur.execute("DELETE FROM etablissements WHERE nom_etablissement != 'Maison d''Hôte'")
            conn.commit()
        
        # 1. Créer des établissements de démonstration
        print("\n🏢 Création des établissements...")
        etablissements_data = [
            {
                'nom': 'Riad Marrakech',
                'pays': 'Morocco',
                'ville': 'Marrakech',
                'telephone': '+212 524 123 456',
                'email': 'contact@riadmarrakech.com',
                'adresse': 'Medina, Marrakech 40000',
                'devise': 'MAD',
                'taxe': 2.5,
                'tva': 20.0,
                'charge': 15.0
            },
            {
                'nom': 'Villa Casablanca',
                'pays': 'Morocco',
                'ville': 'Casablanca',
                'telephone': '+212 522 987 654',
                'email': 'info@villacasa.ma',
                'adresse': 'Ain Diab, Casablanca',
                'devise': 'MAD',
                'taxe': 2.5,
                'tva': 20.0,
                'charge': 12.0
            },
            {
                'nom': 'Hôtel Essaouira',
                'pays': 'Morocco',
                'ville': 'Essaouira',
                'telephone': '+212 524 555 777',
                'email': 'hello@essaouirahotel.com',
                'adresse': 'Boulevard Mohammed V, Essaouira',
                'devise': 'MAD',
                'taxe': 2.5,
                'tva': 20.0,
                'charge': 10.0
            }
        ]
        
        etablissement_ids = []
        for etab in etablissements_data:
            cur.execute('''
                INSERT INTO etablissements (
                    nom_etablissement, pays, ville, telephone, email, adresse,
                    devise, taux_taxe_sejour, taux_tva, taux_charge_plateforme, actif
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                etab['nom'], etab['pays'], etab['ville'], etab['telephone'],
                etab['email'], etab['adresse'], etab['devise'], etab['taxe'],
                etab['tva'], etab['charge'], True
            ))
            result = cur.fetchone()
            etablissement_ids.append(result['id'])
            print(f"  ✅ {etab['nom']} (ID: {result['id']})")
        
        # 2. Créer des chambres pour chaque établissement
        print("\n🛏️ Création des chambres...")
        types_chambres = [
            ('Chambre Standard', 2, 500),
            ('Chambre Deluxe', 2, 750),
            ('Suite Junior', 3, 1200),
            ('Suite Familiale', 4, 1500),
            ('Suite Royale', 2, 2000)
        ]
        
        chambre_ids_by_etab = {}
        for etab_id in etablissement_ids:
            chambre_ids_by_etab[etab_id] = []
            for i, (nom, capacite, prix) in enumerate(types_chambres):
                cur.execute('''
                    INSERT INTO chambres (
                        etablissement_id, nom, capacite, prix_par_nuit, statut
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (etab_id, f"{nom} {i+1}", capacite, prix, 'disponible'))
                result = cur.fetchone()
                chambre_ids_by_etab[etab_id].append(result['id'])
        
        total_chambres = sum(len(chambres) for chambres in chambre_ids_by_etab.values())
        print(f"  ✅ {total_chambres} chambres créées")
        
        # 3. Créer des réservations et clients
        print("\n📅 Création des réservations et clients...")
        
        noms = ['Alami', 'Benali', 'Cohen', 'Dupont', 'Garcia', 'Hassan', 'Ibrahim', 'Johnson', 'Khan', 'Lopez']
        prenoms = ['Ahmed', 'Fatima', 'Mohamed', 'Sarah', 'Youssef', 'Leila', 'Omar', 'Amina', 'Karim', 'Nadia']
        pays = ['Morocco', 'France', 'Spain', 'United Kingdom', 'United States', 'Germany', 'Italy', 'Belgium']
        
        reservations_count = 0
        personnes_count = 0
        
        for etab_id in etablissement_ids:
            chambres = chambre_ids_by_etab[etab_id]
            
            # Créer 5 réservations par établissement
            for i in range(5):
                # Date aléatoire dans les 60 derniers jours
                jours_arriere = random.randint(1, 60)
                date_arrivee = datetime.now() - timedelta(days=jours_arriere)
                nombre_jours = random.randint(2, 7)
                date_depart = date_arrivee + timedelta(days=nombre_jours)
                
                numero_res = f"RES-{date_arrivee.strftime('%Y%m%d')}-{i+1:03d}"
                
                # Créer la réservation
                cur.execute('''
                    INSERT INTO reservations (
                        etablissement_id, numero_reservation, date_arrivee, date_depart,
                        nombre_jours, statut
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    etab_id, numero_res,
                    date_arrivee.date(), date_depart.date(),
                    nombre_jours, random.choice(['active', 'terminee'])
                ))
                result = cur.fetchone()
                reservation_id = result['id']
                reservations_count += 1
                
                # Assigner une ou deux chambres aléatoires
                chambres_selectionnees = random.sample(chambres, random.randint(1, 2))
                
                for chambre_id in chambres_selectionnees:
                    cur.execute('''
                        INSERT INTO reservations_chambres (reservation_id, chambre_id)
                        VALUES (%s, %s)
                    ''', (reservation_id, chambre_id))
                
                # Créer 1-3 personnes pour cette réservation
                nb_personnes = random.randint(1, 3)
                for j in range(nb_personnes):
                    nom = random.choice(noms)
                    prenom = random.choice(prenoms)
                    pays_client = random.choice(pays)
                    
                    cur.execute('''
                        INSERT INTO personnes (
                            reservation_id, chambre_id, est_contact_principal,
                            nom, prenom, email, telephone, pays,
                            type_piece_identite, numero_piece_identite
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        reservation_id,
                        chambres_selectionnees[0],
                        j == 0,
                        nom, prenom,
                        f"{prenom.lower()}.{nom.lower()}@email.com",
                        f"+212 6{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(100, 999)}",
                        pays_client,
                        random.choice(['passeport', 'cin', 'cni']),
                        f"{'PP' if random.random() > 0.5 else 'ID'}{random.randint(100000, 999999)}"
                    ))
                    personnes_count += 1
        
        print(f"  ✅ {reservations_count} réservations créées")
        print(f"  ✅ {personnes_count} clients créés")
        
        # Valider toutes les modifications
        conn.commit()
        print("\n✅ Données de démonstration chargées avec succès!")
        
        # Afficher un résumé
        print(f"\n📊 Résumé:")
        print(f"   - Établissements: {len(etablissement_ids)}")
        print(f"   - Chambres: {total_chambres}")
        print(f"   - Réservations: {reservations_count}")
        print(f"   - Clients: {personnes_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors du chargement des données: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    load_demo_data()
