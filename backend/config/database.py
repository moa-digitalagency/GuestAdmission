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
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS parametres_systeme (
            id SERIAL PRIMARY KEY,
            nom_etablissement VARCHAR(200),
            pays VARCHAR(100),
            adresse TEXT,
            telephone VARCHAR(50),
            email VARCHAR(150),
            devise VARCHAR(10) DEFAULT 'MAD',
            taux_taxe_sejour DECIMAL(5, 2),
            taux_tva DECIMAL(5, 2),
            taux_charge_plateforme DECIMAL(5, 2),
            nombre_chambres INTEGER,
            prix_chambres JSONB,
            logo_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute("SELECT COUNT(*) as count FROM users")
    user_count = cur.fetchone()['count']
    
    if user_count == 0:
        from werkzeug.security import generate_password_hash
        default_password = generate_password_hash('admin123')
        cur.execute('''
            INSERT INTO users (username, password_hash, nom, prenom, role)
            VALUES (%s, %s, %s, %s, %s)
        ''', ('admin', default_password, 'Administrateur', 'Système', 'admin'))
    
    cur.execute("SELECT COUNT(*) as count FROM parametres_systeme")
    param_count = cur.fetchone()['count']
    
    if param_count == 0:
        cur.execute('''
            INSERT INTO parametres_systeme (nom_etablissement, pays, devise, taux_taxe_sejour, taux_tva, taux_charge_plateforme, nombre_chambres, prix_chambres)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', ('Maison d\'Hôte', 'Maroc', 'MAD', 2.5, 20.0, 15.0, 5, '[]'))
    
    conn.commit()
    cur.close()
    conn.close()
