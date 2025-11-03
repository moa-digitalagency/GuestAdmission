#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Ce script doit être exécuté avant le démarrage de l'application
pour s'assurer que toutes les tables et données essentielles existent.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

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

def init_database():
    """Initialiser toutes les tables et données essentielles"""
    print("🔧 Initialisation de la base de données...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Créer la table users
        print("  📋 Création de la table 'users'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nom VARCHAR(100),
                prenom VARCHAR(100),
                email VARCHAR(150),
                role VARCHAR(50) DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table reservations
        print("  📋 Création de la table 'reservations'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id SERIAL PRIMARY KEY,
                date_arrivee DATE NOT NULL,
                date_depart DATE NOT NULL,
                nombre_jours INTEGER,
                sejour_numero VARCHAR(50),
                facture_hebergement DECIMAL(10, 2),
                charge_plateforme DECIMAL(10, 2),
                taxe_sejour DECIMAL(10, 2),
                revenu_mensuel_hebergement DECIMAL(10, 2),
                charges_plateforme_mensuelle DECIMAL(10, 2),
                taxe_sejour_mensuelle DECIMAL(10, 2),
                statut VARCHAR(50) DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table personnes
        print("  📋 Création de la table 'personnes'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS personnes (
                id SERIAL PRIMARY KEY,
                reservation_id INTEGER REFERENCES reservations(id) ON DELETE CASCADE,
                est_contact_principal BOOLEAN DEFAULT FALSE,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                email VARCHAR(150),
                telephone VARCHAR(50),
                pays VARCHAR(100),
                type_piece_identite VARCHAR(50),
                numero_piece_identite VARCHAR(100),
                date_naissance DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table parametres_systeme
        print("  📋 Création de la table 'parametres_systeme'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS parametres_systeme (
                id SERIAL PRIMARY KEY,
                nom_etablissement VARCHAR(200),
                pays VARCHAR(100),
                ville VARCHAR(100),
                adresse TEXT,
                telephone VARCHAR(50),
                whatsapp VARCHAR(50),
                email VARCHAR(150),
                devise VARCHAR(10) DEFAULT 'MAD',
                taux_taxe_sejour DECIMAL(5, 2),
                taux_tva DECIMAL(5, 2),
                taux_charge_plateforme DECIMAL(5, 2),
                nombre_chambres INTEGER,
                prix_chambres JSONB,
                responsables JSONB DEFAULT '[]'::jsonb,
                responsable_nom VARCHAR(100),
                responsable_prenom VARCHAR(100),
                responsable_email VARCHAR(150),
                responsable_telephone VARCHAR(50),
                logo_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vérifier et créer l'utilisateur admin par défaut
        print("  👤 Vérification de l'utilisateur admin...")
        cur.execute("SELECT COUNT(*) as count FROM users")
        result = cur.fetchone()
        user_count = result['count'] if result else 0
        
        if user_count == 0:
            print("  ➕ Création de l'utilisateur admin par défaut...")
            default_password = generate_password_hash('admin123')
            cur.execute('''
                INSERT INTO users (username, password_hash, nom, prenom, role)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('admin', default_password, 'Administrateur', 'Système', 'admin'))
            print("  ✅ Utilisateur admin créé (username: admin, password: admin123)")
        else:
            print(f"  ✅ {user_count} utilisateur(s) déjà présent(s)")
        
        # Vérifier et créer les paramètres système par défaut
        print("  ⚙️  Vérification des paramètres système...")
        cur.execute("SELECT COUNT(*) as count FROM parametres_systeme")
        result = cur.fetchone()
        param_count = result['count'] if result else 0
        
        if param_count == 0:
            print("  ➕ Création des paramètres système par défaut...")
            cur.execute('''
                INSERT INTO parametres_systeme (
                    nom_etablissement, pays, devise, taux_taxe_sejour, 
                    taux_tva, taux_charge_plateforme, nombre_chambres, 
                    prix_chambres, responsables
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                'Maison d\'Hôte', 
                'Maroc', 
                'MAD', 
                2.5, 
                20.0, 
                15.0, 
                5, 
                '[]',
                '[]'
            ))
            print("  ✅ Paramètres système créés")
        else:
            print(f"  ✅ Paramètres système déjà configurés")
        
        # Valider toutes les modifications
        conn.commit()
        print("\n✅ Base de données initialisée avec succès!")
        
        # Afficher un résumé
        cur.execute("SELECT COUNT(*) as count FROM users")
        result = cur.fetchone()
        users = result['count'] if result else 0
        cur.execute("SELECT COUNT(*) as count FROM reservations")
        result = cur.fetchone()
        reservations = result['count'] if result else 0
        cur.execute("SELECT COUNT(*) as count FROM personnes")
        result = cur.fetchone()
        personnes = result['count'] if result else 0
        
        print(f"\n📊 Résumé:")
        print(f"   - Utilisateurs: {users}")
        print(f"   - Réservations: {reservations}")
        print(f"   - Clients: {personnes}")
        print(f"\n🚀 L'application est prête à démarrer!\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de l'initialisation: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    init_database()
