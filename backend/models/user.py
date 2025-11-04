from ..config.database import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, nom, prenom, email, role, etablissement_id=None):
        self.id = id
        self.username = username
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.role = role
        self.etablissement_id = etablissement_id
    
    def is_super_admin(self):
        """Vérifier si l'utilisateur est un super admin"""
        return self.role == 'SUPER_ADMIN'
    
    def is_admin(self):
        """Vérifier si l'utilisateur est un admin (pas super admin)"""
        return self.role == 'admin'
    
    def can_manage_etablissement(self, etablissement_id):
        """Vérifier si l'utilisateur peut gérer un établissement"""
        if self.is_super_admin():
            return True
        return self.has_access_to_etablissement(etablissement_id)
    
    def has_access_to_etablissement(self, etablissement_id):
        """Vérifier si l'utilisateur a accès à un établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT COUNT(*) as count FROM user_etablissements 
            WHERE user_id = %s AND etablissement_id = %s
        ''', (self.id, etablissement_id))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        return result and result['count'] > 0
    
    def get_etablissements(self):
        """Obtenir tous les établissements auxquels l'utilisateur a accès"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        if self.is_super_admin():
            cur.execute('SELECT * FROM etablissements ORDER BY nom_etablissement')
        else:
            cur.execute('''
                SELECT e.* FROM etablissements e
                INNER JOIN user_etablissements ue ON e.id = ue.etablissement_id
                WHERE ue.user_id = %s
                ORDER BY e.nom_etablissement
            ''', (self.id,))
        
        etablissements = cur.fetchall()
        cur.close()
        conn.close()
        
        return etablissements
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user_data = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                nom=user_data['nom'],
                prenom=user_data['prenom'],
                email=user_data['email'],
                role=user_data['role'],
                etablissement_id=user_data.get('etablissement_id')
            )
        return None
    
    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_data = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return user_data
    
    @staticmethod
    def verify_password(username, password):
        user_data = User.get_by_username(username)
        if user_data and check_password_hash(user_data['password_hash'], password):
            return User(
                id=user_data['id'],
                username=user_data['username'],
                nom=user_data['nom'],
                prenom=user_data['prenom'],
                email=user_data['email'],
                role=user_data['role'],
                etablissement_id=user_data.get('etablissement_id')
            )
        return None
    
    @staticmethod
    def create(username, password, nom, prenom, email, role='admin', etablissement_id=None):
        """Créer un nouvel utilisateur"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        password_hash = generate_password_hash(password)
        
        cur.execute('''
            INSERT INTO users (username, password_hash, nom, prenom, email, role, etablissement_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (username, password_hash, nom, prenom, email, role, etablissement_id))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return result['id'] if result else None
    
    @staticmethod
    def add_to_etablissement(user_id, etablissement_id, role='admin'):
        """Ajouter un utilisateur à un établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute('''
                INSERT INTO user_etablissements (user_id, etablissement_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, etablissement_id) DO NOTHING
            ''', (user_id, etablissement_id, role))
            
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return False
    
    @staticmethod
    def remove_from_etablissement(user_id, etablissement_id):
        """Retirer un utilisateur d'un établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            DELETE FROM user_etablissements 
            WHERE user_id = %s AND etablissement_id = %s
        ''', (user_id, etablissement_id))
        
        conn.commit()
        cur.close()
        conn.close()
    
    @staticmethod
    def get_users_by_etablissement(etablissement_id):
        """Obtenir tous les utilisateurs d'un établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT u.*, ue.role as etablissement_role
            FROM users u
            INNER JOIN user_etablissements ue ON u.id = ue.user_id
            WHERE ue.etablissement_id = %s
            ORDER BY u.nom, u.prenom
        ''', (etablissement_id,))
        
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        return users
    
    @staticmethod
    def update_current_etablissement(user_id, etablissement_id):
        """Mettre à jour l'établissement actuel de l'utilisateur"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            UPDATE users 
            SET etablissement_id = %s 
            WHERE id = %s
        ''', (etablissement_id, user_id))
        
        conn.commit()
        cur.close()
        conn.close()
