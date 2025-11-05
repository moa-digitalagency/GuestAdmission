#!/usr/bin/env python3
"""
Migration 005: Renforcer l'isolation des données par tenant
- Ajouter des indexes supplémentaires pour améliorer les performances de filtrage
- Ajouter des contraintes pour garantir l'intégrité des données
- S'assurer que activity_logs peut être filtré par tenant
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
    print("🔧 Migration 005: Renforcement de l'isolation tenant...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Ajouter des indexes pour améliorer les performances des requêtes filtrées par tenant
        print("  📋 Ajout d'indexes pour l'optimisation des requêtes tenant...")
        
        # Index sur chambres pour le filtrage par établissement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_chambres_etablissement_id 
            ON chambres(etablissement_id)
        ''')
        
        # Index sur reservations pour le filtrage par établissement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_reservations_etablissement_id 
            ON reservations(etablissement_id)
        ''')
        
        # Index sur extras pour le filtrage par établissement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_extras_etablissement_id 
            ON extras(etablissement_id)
        ''')
        
        # Index sur personnels pour le filtrage par établissement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_personnels_etablissement_id 
            ON personnels(etablissement_id)
        ''')
        
        # Index sur mail_configs pour le filtrage par établissement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_mail_configs_etablissement_id 
            ON mail_configs(etablissement_id)
        ''')
        
        # Index sur calendriers_ical pour le filtrage par établissement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_calendriers_ical_etablissement_id 
            ON calendriers_ical(etablissement_id)
        ''')
        
        # 2. Ajouter etablissement_id dans activity_logs pour faciliter le filtrage par tenant
        print("  📋 Ajout de etablissement_id dans activity_logs...")
        cur.execute('''
            ALTER TABLE activity_logs 
            ADD COLUMN IF NOT EXISTS etablissement_id INTEGER 
            REFERENCES etablissements(id) ON DELETE SET NULL
        ''')
        
        # Index pour activity_logs
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_logs_etablissement_id 
            ON activity_logs(etablissement_id)
        ''')
        
        # 3. Ajouter un index composite pour améliorer les requêtes courantes
        print("  📋 Ajout d'indexes composites...")
        
        # Index composite pour les réservations actives par établissement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_reservations_etablissement_statut 
            ON reservations(etablissement_id, statut)
        ''')
        
        # Index composite pour les extras actifs par établissement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_extras_etablissement_actif 
            ON extras(etablissement_id, actif)
        ''')
        
        # Index composite pour user_etablissements
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_etablissements_etablissement_role 
            ON user_etablissements(etablissement_id, role)
        ''')
        
        # 4. Ajouter une colonne pour marquer les établissements de démonstration
        print("  📋 Ajout de colonne is_demo dans etablissements...")
        cur.execute('''
            ALTER TABLE etablissements 
            ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE
        ''')
        
        # 5. Ajouter une colonne last_activity dans tenant_accounts
        print("  📋 Ajout de last_activity dans tenant_accounts...")
        cur.execute('''
            ALTER TABLE tenant_accounts 
            ADD COLUMN IF NOT EXISTS last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ''')
        
        conn.commit()
        print("\n✅ Migration 005 terminée avec succès!")
        print("\nℹ️  Notes:")
        print("  - Indexes ajoutés pour améliorer les performances des requêtes filtrées par tenant")
        print("  - activity_logs peut maintenant être filtré par établissement")
        print("  - Indexes composites créés pour les requêtes courantes")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate()
