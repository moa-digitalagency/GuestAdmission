#!/usr/bin/env python3
"""
Migration 003: Corriger les associations user-établissement incorrectes
- Supprimer toutes les associations créées par erreur lors de la migration 002
- Nettoyer etablissement_id des utilisateurs non-SUPER_ADMIN
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
    """Exécuter la migration de correction"""
    print("🔧 Migration 003: Correction des associations user-établissement...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Supprimer TOUTES les associations user-établissement existantes
        # Les bonnes associations seront créées via l'interface super admin
        print("  🧹 Suppression des associations user-établissement incorrectes...")
        cur.execute('DELETE FROM user_etablissements')
        
        # 2. Réinitialiser etablissement_id pour tous les utilisateurs non-SUPER_ADMIN
        print("  🧹 Réinitialisation de etablissement_id...")
        cur.execute('''
            UPDATE users 
            SET etablissement_id = NULL 
            WHERE role != 'SUPER_ADMIN'
        ''')
        
        conn.commit()
        print("\n✅ Migration 003 terminée avec succès!")
        print("  ℹ️  Les associations user-établissement doivent maintenant être créées via l'interface super admin")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate()
