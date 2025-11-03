"""
Point d'entrée principal de l'application
Ce fichier importe l'application Flask après avoir initialisé la base de données
"""

from backend.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
