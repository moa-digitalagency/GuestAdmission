from ..config.database import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, nom, prenom, email, role):
        self.id = id
        self.username = username
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.role = role
    
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
                role=user_data['role']
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
                role=user_data['role']
            )
        return None
