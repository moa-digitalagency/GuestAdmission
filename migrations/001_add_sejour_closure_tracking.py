#!/usr/bin/env python3
"""
Migration: Add closure tracking to reservations
Adds closed_at and closed_by fields to track when a séjour is finalized
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL n'est pas défini")
        sys.exit(1)
    
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def migrate():
    print("🔄 Migration: Ajout du suivi de clôture des séjours...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Add closed_at field
        print("  📋 Ajout du champ 'closed_at' à reservations...")
        cur.execute('''
            ALTER TABLE reservations 
            ADD COLUMN IF NOT EXISTS closed_at TIMESTAMP NULL
        ''')
        
        # Add closed_by field (tracks which user closed the séjour)
        print("  📋 Ajout du champ 'closed_by' à reservations...")
        cur.execute('''
            ALTER TABLE reservations 
            ADD COLUMN IF NOT EXISTS closed_by INTEGER REFERENCES users(id) ON DELETE SET NULL
        ''')
        
        # Add index on statut for faster queries
        print("  📋 Ajout d'index sur le statut...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_reservations_statut 
            ON reservations(statut)
        ''')
        
        # Add index on etablissement_id for statistics
        print("  📋 Ajout d'index sur etablissement_id...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_reservations_etablissement 
            ON reservations(etablissement_id)
        ''')
        
        # Add index on date fields for date range queries
        print("  📋 Ajout d'index sur les dates...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_reservations_dates 
            ON reservations(date_arrivee, date_depart)
        ''')
        
        # Add index on personnes pays for country statistics
        print("  📋 Ajout d'index sur pays dans personnes...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_personnes_pays 
            ON personnes(pays)
        ''')
        
        # Add index on sejours_extras for faster queries
        print("  📋 Ajout d'index sur sejours_extras...")
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_sejours_extras_reservation 
            ON sejours_extras(reservation_id)
        ''')
        
        conn.commit()
        print("✅ Migration terminée avec succès!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate()
