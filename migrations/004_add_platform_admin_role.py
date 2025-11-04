#!/usr/bin/env python3
"""
Migration 004: Transformer l'application en SaaS avec PLATFORM_ADMIN
- Transformer le rôle SUPER_ADMIN existant en PLATFORM_ADMIN
- PLATFORM_ADMIN = Admin de la plateforme (niveau le plus élevé)
- admin = Admin d'établissement (tenant admin)
- Ajouter une table pour tracker les comptes clients (tenants)
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
    print("🔧 Migration 004: Transformation en SaaS avec PLATFORM_ADMIN...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Créer une table pour les comptes clients (tenants)
        print("  📋 Création de la table 'tenant_accounts'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tenant_accounts (
                id SERIAL PRIMARY KEY,
                nom_compte VARCHAR(255) NOT NULL,
                primary_admin_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actif BOOLEAN DEFAULT TRUE,
                notes TEXT,
                UNIQUE(nom_compte)
            )
        ''')
        
        # 2. Ajouter une colonne tenant_account_id dans etablissements
        print("  📋 Ajout de la colonne 'tenant_account_id' dans etablissements...")
        cur.execute('''
            ALTER TABLE etablissements 
            ADD COLUMN IF NOT EXISTS tenant_account_id INTEGER 
            REFERENCES tenant_accounts(id) ON DELETE CASCADE
        ''')
        
        # 3. Transformer SUPER_ADMIN en PLATFORM_ADMIN
        print("  👤 Transformation du rôle SUPER_ADMIN en PLATFORM_ADMIN...")
        cur.execute('''
            UPDATE users 
            SET role = 'PLATFORM_ADMIN' 
            WHERE role = 'SUPER_ADMIN'
        ''')
        
        # 4. Créer un index sur tenant_account_id
        print("  📋 Création de l'index sur tenant_account_id...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_etablissements_tenant_account_id 
            ON etablissements(tenant_account_id)
        ''')
        
        # 5. Ajouter une colonne pour distinguer l'admin principal d'un tenant
        print("  📋 Ajout de la colonne 'is_primary_admin' dans user_etablissements...")
        cur.execute('''
            ALTER TABLE user_etablissements 
            ADD COLUMN IF NOT EXISTS is_primary_admin BOOLEAN DEFAULT FALSE
        ''')
        
        conn.commit()
        print("\n✅ Migration 004 terminée avec succès!")
        print("\nℹ️  Notes:")
        print("  - Le rôle SUPER_ADMIN a été transformé en PLATFORM_ADMIN")
        print("  - PLATFORM_ADMIN = Admin de la plateforme (crée des comptes clients)")
        print("  - admin = Admin d'établissement (gère ses établissements)")
        print("  - Les comptes clients (tenants) peuvent avoir plusieurs établissements")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate()
