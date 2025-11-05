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
                etablissement_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table tenant_accounts (comptes clients)
        print("  📋 Création de la table 'tenant_accounts'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tenant_accounts (
                id SERIAL PRIMARY KEY,
                nom_compte VARCHAR(200) NOT NULL,
                primary_admin_user_id INTEGER,
                notes TEXT,
                actif BOOLEAN DEFAULT TRUE,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table etablissements
        print("  📋 Création de la table 'etablissements'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS etablissements (
                id SERIAL PRIMARY KEY,
                tenant_account_id INTEGER REFERENCES tenant_accounts(id) ON DELETE CASCADE,
                nom_etablissement VARCHAR(200) NOT NULL,
                numero_identification VARCHAR(100),
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
                logo_url VARCHAR(500),
                format_numero_reservation VARCHAR(100) DEFAULT 'RES-{YYYY}{MM}{DD}-{NUM}',
                prochain_numero_sequence INTEGER DEFAULT 1,
                mode_tarification VARCHAR(20) DEFAULT 'CHAMBRE' CHECK (mode_tarification IN ('CHAMBRE', 'ETABLISSEMENT')),
                prix_global_nuitee DECIMAL(10, 2),
                actif BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table chambres (doit être créée avant reservations pour la FK)
        print("  📋 Création de la table 'chambres'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS chambres (
                id SERIAL PRIMARY KEY,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE CASCADE,
                nom VARCHAR(100) NOT NULL,
                type_chambre VARCHAR(100),
                description TEXT,
                capacite INTEGER DEFAULT 2,
                prix_par_nuit DECIMAL(10, 2),
                statut VARCHAR(50) DEFAULT 'disponible',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table reservations
        print("  📋 Création de la table 'reservations'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id SERIAL PRIMARY KEY,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE CASCADE,
                numero_reservation VARCHAR(100) UNIQUE,
                date_arrivee DATE NOT NULL,
                date_depart DATE NOT NULL,
                nombre_jours INTEGER,
                facture_hebergement DECIMAL(10, 2),
                charge_plateforme DECIMAL(10, 2),
                taxe_sejour DECIMAL(10, 2),
                revenu_mensuel_hebergement DECIMAL(10, 2),
                charges_plateforme_mensuelle DECIMAL(10, 2),
                taxe_sejour_mensuelle DECIMAL(10, 2),
                statut VARCHAR(50) DEFAULT 'active',
                observations TEXT,
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
                chambre_id INTEGER REFERENCES chambres(id) ON DELETE SET NULL,
                est_contact_principal BOOLEAN DEFAULT FALSE,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                email VARCHAR(150),
                telephone VARCHAR(50),
                pays VARCHAR(100),
                ville VARCHAR(100),
                type_piece_identite VARCHAR(50),
                numero_piece_identite VARCHAR(100),
                date_naissance DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table reservations_chambres (relation many-to-many)
        print("  📋 Création de la table 'reservations_chambres'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reservations_chambres (
                id SERIAL PRIMARY KEY,
                reservation_id INTEGER REFERENCES reservations(id) ON DELETE CASCADE,
                chambre_id INTEGER REFERENCES chambres(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(reservation_id, chambre_id)
            )
        ''')
        
        # Créer la table extras
        print("  📋 Création de la table 'extras'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS extras (
                id SERIAL PRIMARY KEY,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE CASCADE,
                nom VARCHAR(200) NOT NULL,
                description TEXT,
                prix_unitaire DECIMAL(10, 2) NOT NULL,
                unite VARCHAR(50) DEFAULT 'unité',
                actif BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table sejours_extras (relation many-to-many)
        print("  📋 Création de la table 'sejours_extras'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sejours_extras (
                id SERIAL PRIMARY KEY,
                reservation_id INTEGER REFERENCES reservations(id) ON DELETE CASCADE,
                extra_id INTEGER REFERENCES extras(id) ON DELETE CASCADE,
                quantite DECIMAL(10, 2) NOT NULL DEFAULT 1,
                prix_unitaire DECIMAL(10, 2) NOT NULL,
                montant_total DECIMAL(10, 2) NOT NULL,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Créer la table personnels
        print("  📋 Création de la table 'personnels'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS personnels (
                id SERIAL PRIMARY KEY,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE CASCADE,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                email VARCHAR(150),
                telephone VARCHAR(50),
                poste VARCHAR(100),
                salaire DECIMAL(10, 2),
                date_embauche DATE,
                acces_dashboard BOOLEAN DEFAULT FALSE,
                acces_sejours BOOLEAN DEFAULT FALSE,
                acces_clients BOOLEAN DEFAULT FALSE,
                acces_extras BOOLEAN DEFAULT FALSE,
                acces_statistiques BOOLEAN DEFAULT FALSE,
                acces_parametres BOOLEAN DEFAULT FALSE,
                actif BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table parametres_systeme (pour compatibilité, mais déprécié)
        print("  📋 Création de la table 'parametres_systeme'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS parametres_systeme (
                id SERIAL PRIMARY KEY,
                nom_etablissement VARCHAR(200),
                numero_identification VARCHAR(100),
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
                format_numero_reservation VARCHAR(100) DEFAULT 'RES-{YYYY}{MM}{DD}-{NUM}',
                prochain_numero_sequence INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table mail_configs pour la messagerie
        print("  📋 Création de la table 'mail_configs'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS mail_configs (
                id SERIAL PRIMARY KEY,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE CASCADE,
                nom_config VARCHAR(255) NOT NULL,
                email_address VARCHAR(255) NOT NULL,
                smtp_host VARCHAR(255) NOT NULL,
                smtp_port INTEGER NOT NULL DEFAULT 587,
                smtp_username VARCHAR(255) NOT NULL,
                smtp_password VARCHAR(255) NOT NULL,
                smtp_use_tls BOOLEAN DEFAULT TRUE,
                pop_host VARCHAR(255),
                pop_port INTEGER DEFAULT 995,
                pop_username VARCHAR(255),
                pop_password VARCHAR(255),
                pop_use_ssl BOOLEAN DEFAULT TRUE,
                actif BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table emails pour stocker les messages
        print("  📋 Création de la table 'emails'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id SERIAL PRIMARY KEY,
                mail_config_id INTEGER REFERENCES mail_configs(id) ON DELETE CASCADE,
                message_id VARCHAR(255) UNIQUE,
                subject TEXT,
                from_email VARCHAR(255),
                to_email TEXT,
                cc_email TEXT,
                bcc_email TEXT,
                body_text TEXT,
                body_html TEXT,
                folder VARCHAR(50) DEFAULT 'inbox',
                is_read BOOLEAN DEFAULT FALSE,
                is_starred BOOLEAN DEFAULT FALSE,
                has_attachments BOOLEAN DEFAULT FALSE,
                date_sent TIMESTAMP,
                date_received TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_email_indexed VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table calendriers_ical pour la synchronisation
        print("  📋 Création de la table 'calendriers_ical'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS calendriers_ical (
                id SERIAL PRIMARY KEY,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE CASCADE,
                nom VARCHAR(200) NOT NULL,
                plateforme VARCHAR(50) NOT NULL,
                ical_url TEXT NOT NULL,
                derniere_synchronisation TIMESTAMP,
                statut_derniere_synchro VARCHAR(50) DEFAULT 'jamais',
                message_erreur TEXT,
                actif BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table reservations_ical
        print("  📋 Création de la table 'reservations_ical'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reservations_ical (
                id SERIAL PRIMARY KEY,
                calendrier_id INTEGER REFERENCES calendriers_ical(id) ON DELETE CASCADE,
                uid_ical VARCHAR(500) UNIQUE NOT NULL,
                titre VARCHAR(300),
                date_debut DATE NOT NULL,
                date_fin DATE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ajouter la colonne closed_at dans reservations si elle n'existe pas
        print("  📋 Ajout de la colonne 'closed_at' dans reservations...")
        cur.execute('''
            ALTER TABLE reservations 
            ADD COLUMN IF NOT EXISTS closed_at TIMESTAMP
        ''')
        
        # Créer la table user_etablissements pour lier les utilisateurs aux établissements
        print("  📋 Création de la table 'user_etablissements'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_etablissements (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE CASCADE,
                role VARCHAR(50) DEFAULT 'user',
                is_primary_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, etablissement_id)
            )
        ''')
        
        # Créer la table activity_logs pour le suivi des activités
        print("  📋 Création de la table 'activity_logs'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                username VARCHAR(100),
                action VARCHAR(100) NOT NULL,
                route VARCHAR(500) NOT NULL,
                method VARCHAR(10) NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                status_code INTEGER,
                details JSONB,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer des index pour améliorer les performances des requêtes
        print("  📋 Création des index sur 'activity_logs'...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id)
        ''')
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at DESC)
        ''')
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action)
        ''')
        
        # Vérifier et créer l'utilisateur admin par défaut
        print("  👤 Vérification de l'utilisateur admin...")
        cur.execute("SELECT COUNT(*) as count FROM users")
        result = cur.fetchone()
        user_count = result['count'] if result else 0
        
        if user_count == 0:
            print("  ➕ Création de l'utilisateur PLATFORM_ADMIN par défaut...")
            default_password = generate_password_hash('admin123')
            cur.execute('''
                INSERT INTO users (username, password_hash, nom, prenom, role, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', ('admin', default_password, 'Administrateur', 'Plateforme', 'PLATFORM_ADMIN', 'admin@platform.com'))
            print("  ✅ Utilisateur PLATFORM_ADMIN créé (username: admin, password: admin123)")
        else:
            print(f"  ✅ {user_count} utilisateur(s) déjà présent(s)")
        
        # Vérifier et créer l'établissement par défaut
        print("  🏢 Vérification des établissements...")
        cur.execute("SELECT COUNT(*) as count FROM etablissements")
        result = cur.fetchone()
        etablissement_count = result['count'] if result else 0
        
        if etablissement_count == 0:
            print("  ➕ Création de l'établissement par défaut...")
            cur.execute('''
                INSERT INTO etablissements (
                    nom_etablissement, pays, devise, taux_taxe_sejour, 
                    taux_tva, taux_charge_plateforme, actif
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                'Maison d\'Hôte', 
                'Maroc', 
                'MAD', 
                2.5, 
                20.0, 
                15.0,
                True
            ))
            result = cur.fetchone()
            etablissement_id = result['id'] if result else None
            print(f"  ✅ Établissement créé (ID: {etablissement_id})")
        else:
            print(f"  ✅ {etablissement_count} établissement(s) déjà présent(s)")
        
        # Vérifier et créer les paramètres système par défaut (pour compatibilité)
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
