# Maison d'Hôte - Système de Gestion

## Vue d'ensemble
Application Flask de gestion de maison d'hôte avec gestion complète des établissements, réservations, et clients.

## État du projet - 3 novembre 2025

### ✅ Restructuration complétée
- Migration terminologie: "Réservations" → "Séjours" dans toute l'application
- Nouvelle page Statistiques dédiée créée
- Page Paramètres restructurée avec sections Chambres et Personnels
- Navigation mise à jour avec lien vers Statistiques
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
  - `sejours.py` - Gestion des séjours et clients (anciennement reservations.py)
  - `parametres.py` - Paramètres système
  - `data_management.py` - Chargement demo et réinitialisation

#### Frontend
- **Templates**: `frontend/templates/`
  - `base_dashboard.html` - Template de base avec sidebar et navigation
  - `login.html` - Page de connexion
  - `dashboard.html` - Tableau de bord
  - `statistiques.html` - Page statistiques dédiée
  - `parametres.html` - Page paramètres (Établissements, Chambres, Personnels)
  - `nouveau_sejour.html` - Créer un séjour (anciennement nouvelle_reservation.html)
  - `sejours.html` - Liste des séjours (anciennement reservations.html)
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

2. **Gestion des séjours**
   - Création de séjours
   - Association chambres
   - Gestion clients/personnes
   - Numérotation automatique

3. **Statistiques** (Page dédiée)
   - Vue d'ensemble des séjours
   - Statistiques clients
   - Métriques établissements
   - Occupation des chambres

4. **Paramètres système**
   - Gestion établissements
   - Gestion chambres
   - Gestion personnels
   - Chargement données demo
   - Réinitialisation sélective/complète

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

1. **Migration terminologie complète**:
   - Toutes les mentions "Réservations" → "Séjours"
   - Routes: `/reservations` → `/sejours`
   - API: `/api/reservations` → `/api/sejours`
   - Templates renommés et mis à jour

2. **Nouvelle page Statistiques**:
   - Page dédiée aux statistiques (`/statistiques`)
   - Graphiques et métriques en temps réel
   - Données séjours, clients, établissements, chambres
   - Navigation mise à jour avec icône 📈

3. **Restructuration page Paramètres**:
   - Section "Mes Établissements" conservée
   - Nouvelle section "Chambres" avec liste et gestion
   - Nouvelle section "Personnels" (en développement)
   - Suppression de la section statistiques (déplacée vers page dédiée)
   - Section "Mon compte" et "Gestion des données" conservées

4. **Chargement des données**:
   - Script `load_demo_data.py` testé et fonctionnel
   - Crée 3 établissements demo (Riad Marrakech, Villa Casablanca, Hôtel Essaouira)
   - Génère 15 séjours et 29 clients
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

1. **Améliorations terminologie**:
   - Renommer les fonctions database comme `format_numero_reservation` → `format_numero_sejour`
   - Uniformiser les préfixes (RES- → SEJ- pour les numéros de séjours)

2. **Tests fonctionnels**:
   - Tester le flux complet de création d'un séjour
   - Valider la page Statistiques avec données réelles
   - Tester la gestion des chambres dans Paramètres

3. **Développement futur**:
   - Compléter la section Personnels avec gestion des droits
   - Ajouter formulaires d'édition pour les chambres
   - Développer les API personnels (/api/personnels)
