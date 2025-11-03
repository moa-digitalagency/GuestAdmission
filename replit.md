# Maison d'Hôte - Système de Gestion

## Vue d'ensemble
Application Flask de gestion de maison d'hôte avec gestion complète des établissements, réservations, et clients.

## État du projet - 3 novembre 2025

### ✅ Migration complétée
- Tous les packages Python installés et configurés
- Base de données PostgreSQL initialisée
- Application déployée et fonctionnelle sur le port 5000
- Workflow configuré avec gunicorn

### 📊 Données actuelles
- **Utilisateurs**: 1 (admin)
- **Établissements**: 4 (incluant 3 établissements demo)
- **Réservations**: 15
- **Clients**: 29
- **Chambres**: 15

### 🔑 Identifiants administrateur
- **Username**: admin
- **Password**: admin123

### 🏗️ Architecture

#### Backend (Flask)
- **App principal**: `backend/app.py`
- **Routes**:
  - `auth.py` - Authentification et gestion utilisateurs
  - `etablissements.py` - Gestion des établissements
  - `chambres.py` - Gestion des chambres
  - `reservations.py` - Gestion des réservations et clients
  - `parametres.py` - Paramètres système
  - `data_management.py` - Chargement demo et réinitialisation

#### Frontend
- **Templates**: `frontend/templates/`
  - `base_dashboard.html` - Template de base avec sidebar
  - `login.html` - Page de connexion
  - `dashboard.html` - Tableau de bord
  - `parametres.html` - Page paramètres
  - `nouvelle_reservation.html` - Créer une réservation
  - `reservations.html` - Liste des réservations
  - `clients_list.html` - Liste des clients

- **Static**: `frontend/static/`
  - `css/styles.css` - Styles CSS avec sections dotted
  - `data/countries.json` - Liste des pays et villes

### 🔧 Fonctionnalités

1. **Gestion des établissements**
   - Création/modification/suppression
   - Support multi-établissements
   - Upload de logo
   - Activation/désactivation

2. **Gestion des réservations**
   - Création de réservations
   - Association chambres
   - Gestion clients/personnes
   - Numérotation automatique

3. **Paramètres système**
   - Configuration établissements
   - Chargement données demo
   - Réinitialisation sélective/complète
   - Statistiques

### 🚀 Démarrage

L'application démarre automatiquement via le workflow "Start application" qui:
1. Initialise la base de données (via `init_database.py`)
2. Lance gunicorn sur le port 5000

### 📝 Commandes utiles

```bash
# Charger les données de démonstration
python3 load_demo_data.py --force

# Accéder à la base de données
psql $DATABASE_URL

# Redémarrer l'application
# Via le workflow dans l'interface Replit
```

### 🐛 Débogage page paramètres

Si la page paramètres n'affiche pas les données:

1. **Vérifier la console du navigateur** (F12)
   - Rechercher les messages de débogage commençant par 🚀, 📁, 🏢, 📊
   - Vérifier les erreurs JavaScript

2. **Vérifier l'authentification**
   - S'assurer d'être connecté avec admin/admin123
   - Vérifier que la session est active

3. **Tester les APIs manuellement**
   ```bash
   # Se connecter et récupérer le cookie
   curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}' \
     -c cookies.txt
   
   # Tester l'API établissements
   curl http://localhost:5000/api/etablissements?actif_only=false \
     -b cookies.txt
   ```

### 🔄 Dernières modifications (3 novembre 2025)

1. **Page paramètres**:
   - Ajout de gestion d'erreurs robuste
   - Messages d'erreur clairs pour l'utilisateur
   - Débogage console amélioré avec emojis
   - Validation des réponses API

2. **Chargement des données**:
   - Script `load_demo_data.py` testé et fonctionnel
   - Crée 3 établissements demo (Riad Marrakech, Villa Casablanca, Hôtel Essaouira)
   - Génère 15 réservations et 29 clients
   - 15 chambres de différents types

### 📚 Stack technique

- **Backend**: Flask 3.1, SQLAlchemy, Flask-Login
- **Base de données**: PostgreSQL (via Neon)
- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **Serveur**: Gunicorn
- **Environnement**: Python 3.11

### 🎨 Design

- Interface moderne avec sections en "dotted border"
- Couleurs thématiques (bleu, vert, violet, orange)
- Responsive design
- Sidebar navigation
- Alerts et notifications

## Prochaines étapes recommandées

1. Vérifier que le fichier `frontend/static/data/countries.json` existe et contient les données
2. Tester la page paramètres en ouvrant la console navigateur pour voir les messages de débogage
3. Si nécessaire, créer le fichier countries.json avec la liste des pays
