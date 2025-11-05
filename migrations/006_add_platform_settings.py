#!/usr/bin/env python3
"""
Migration 006: Ajouter une table pour les paramètres de la plateforme
- Permet au PLATFORM_ADMIN de gérer le nom de la plateforme et autres paramètres globaux
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

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

def migrate():
    """Exécuter la migration"""
    print("🔧 Migration 006: Ajout de la table platform_settings...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Créer la table platform_settings
        print("  📋 Création de la table 'platform_settings'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS platform_settings (
                id SERIAL PRIMARY KEY,
                platform_name VARCHAR(255) NOT NULL DEFAULT 'Maison d''Hôte',
                platform_logo_url TEXT,
                support_email VARCHAR(255),
                support_phone VARCHAR(50),
                default_currency VARCHAR(10) DEFAULT 'MAD',
                default_language VARCHAR(10) DEFAULT 'fr',
                maintenance_mode BOOLEAN DEFAULT FALSE,
                maintenance_message TEXT,
                custom_css TEXT,
                custom_js TEXT,
                meta_title VARCHAR(255),
                meta_description TEXT,
                meta_keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vérifier si une ligne existe déjà
        cur.execute('SELECT COUNT(*) as count FROM platform_settings')
        count = cur.fetchone()['count']
        
        if count == 0:
            print("  ➕ Insertion des paramètres par défaut...")
            cur.execute('''
                INSERT INTO platform_settings (
                    platform_name,
                    support_email,
                    default_currency,
                    default_language,
                    meta_title,
                    meta_description
                ) VALUES (
                    'Maison d''Hôte - Système de Gestion',
                    'support@example.com',
                    'MAD',
                    'fr',
                    'Maison d''Hôte - Gestion Multi-Tenant',
                    'Plateforme SaaS de gestion pour maisons d''hôtes'
                )
            ''')
        
        # Créer un index pour l'optimisation
        print("  📋 Création d'index...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_platform_settings_updated 
            ON platform_settings(updated_at DESC)
        ''')
        
        conn.commit()
        print("\n✅ Migration 006 terminée avec succès!")
        print("\nℹ️  Notes:")
        print("  - Table platform_settings créée pour gérer les paramètres globaux")
        print("  - Le PLATFORM_ADMIN peut maintenant configurer le nom de la plateforme")
        print("  - Support pour personnalisation CSS/JS et mode maintenance")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate()
