import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """
    Obtenir une connexion à la base de données PostgreSQL
    
    Returns:
        psycopg2.connection: Connexion à la base de données avec RealDictCursor
    """
    conn = psycopg2.connect(
        os.environ['DATABASE_URL'],
        cursor_factory=RealDictCursor
    )
    return conn
