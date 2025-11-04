#!/usr/bin/env python3
"""
Migration 002: Ajouter le support multi-tenant
- Ajouter la table user_etablissements pour gérer les associations
- Ajouter etablissement_id dans users pour l'établissement actuel
- Mettre à jour le rôle admin par défaut en SUPER_ADMIN
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
    print("🔧 Migration 002: Ajout du support multi-tenant...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Créer la table user_etablissements pour la relation many-to-many
        print("  📋 Création de la table 'user_etablissements'...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_etablissements (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                etablissement_id INTEGER REFERENCES etablissements(id) ON DELETE CASCADE,
                role VARCHAR(50) DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, etablissement_id)
            )
        ''')
        
        # 2. Ajouter l'index pour améliorer les performances
        print("  📋 Création des index...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_etablissements_user_id 
            ON user_etablissements(user_id)
        ''')
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_etablissements_etablissement_id 
            ON user_etablissements(etablissement_id)
        ''')
        
        # 3. Ajouter la colonne etablissement_id dans users (établissement actuel)
        print("  📋 Ajout de la colonne 'etablissement_id' dans users...")
        cur.execute('''
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS etablissement_id INTEGER 
            REFERENCES etablissements(id) ON DELETE SET NULL
        ''')
        
        # 4. Mettre à jour le rôle du premier utilisateur en SUPER_ADMIN
        print("  👤 Mise à jour de l'utilisateur admin par défaut en SUPER_ADMIN...")
        cur.execute('''
            UPDATE users 
            SET role = 'SUPER_ADMIN' 
            WHERE id = 1 AND role = 'admin'
        ''')
        
        # 5. Pour les utilisateurs non-SUPER_ADMIN existants, ne PAS créer d'associations automatiques
        # Les associations seront créées via l'interface super admin
        print("  ℹ️  Les associations user-établissement seront créées via l'interface super admin")
        
        # 6. Pas de mise à jour automatique de etablissement_id
        # Cela sera géré lors de la création de nouveaux utilisateurs via l'interface
        print("  ℹ️  etablissement_id sera défini lors de la création de nouveaux utilisateurs")
        
        conn.commit()
        print("\n✅ Migration 002 terminée avec succès!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate()
