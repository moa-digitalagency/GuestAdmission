import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        os.environ['DATABASE_URL'],
        cursor_factory=RealDictCursor
    )
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            nom VARCHAR(100) NOT NULL,
            prenom VARCHAR(100) NOT NULL,
            mail VARCHAR(150),
            pays VARCHAR(100),
            tel VARCHAR(50),
            arrivee DATE,
            depart DATE,
            sejour_numero VARCHAR(50),
            facture_hebergement DECIMAL(10, 2),
            charge_plateforme DECIMAL(10, 2),
            taxe_sejour DECIMAL(10, 2),
            revenu_mensuel_hebergement DECIMAL(10, 2),
            charges_plateforme_mensuelle DECIMAL(10, 2),
            taxe_sejour_mensuelle DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
