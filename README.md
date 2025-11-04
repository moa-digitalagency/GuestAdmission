# 🏡 Maison d'Hôte - Système de Gestion

Application web professionnelle de gestion d'établissement d'hébergement (maison d'hôte) avec design system MOA.

## 📋 Description

Système complet de gestion pour maisons d'hôtes permettant de :
- Gérer les réservations et les clients
- Calculer automatiquement les tarifs, taxes et charges
- Suivre les statistiques et le tableau de bord
- Configurer les paramètres de l'établissement
- Base de données clients complète

## 🎨 Design System

Cette application utilise le **MOA Design System** développé par MOA Digital Agency LLC :
- Bordures pointillées (3px dotted) signature MOA
- Sections colorées avec codes couleur sémantiques
- Boutons avec bordures solides (2px)
- Typographie compacte et professionnelle
- Badges avec bordures pill-shaped
- Design responsive mobile-first

## 🚀 Démarrage rapide

### Prérequis
- Python 3.11+
- PostgreSQL
- uv (gestionnaire de paquets Python)

### Installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd workspace
```

2. **Installer les dépendances**
```bash
uv sync
```

3. **Configurer la base de données**

Créer une base de données PostgreSQL et définir la variable d'environnement :
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

4. **Initialiser la base de données**
```bash
uv run python -c "from backend.config.database import init_db; init_db()"
```

5. **Lancer l'application**
```bash
gunicorn --bind 0.0.0.0:5000 --reload backend.app:app
```

L'application sera accessible sur : `http://localhost:5000`

## 👤 Connexion par défaut

- **Nom d'utilisateur** : `admin`
- **Mot de passe** : `admin123`

## 📁 Structure du projet

```
workspace/
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py          # Configuration base de données
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # Modèle utilisateur
│   │   ├── client.py            # Modèle client
│   │   ├── personne.py          # Modèle personne
│   │   └── reservation.py       # Modèle réservation
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Routes authentification
│   │   ├── clients.py           # Routes clients
│   │   ├── reservations.py      # Routes réservations
│   │   ├── parametres.py        # Routes paramètres
│   │   ├── countries.py         # Routes pays
│   │   └── cities.py            # Routes villes
│   ├── __init__.py
│   ├── app.py                   # Application Flask principale
│   └── utils.py                 # Utilitaires
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css       # Styles MOA Design System
│   │   └── data/
│   │       └── countries.json   # Données pays
│   └── templates/
│       ├── base.html
│       ├── base_dashboard.html
│       ├── login.html
│       ├── dashboard.html
│       ├── nouvelle_reservation.html
│       ├── reservations.html
│       ├── clients_list.html
│       └── parametres.html
├── pyproject.toml               # Configuration du projet
├── requirements.txt             # Dépendances Python
└── README.md                    # Ce fichier
```

## 🛠️ Technologies utilisées

- **Backend** : Flask 3.1.2, Flask-Login, Flask-CORS, Flask-SQLAlchemy
- **Base de données** : PostgreSQL (avec psycopg2-binary)
- **Serveur web** : Gunicorn 23.0.0
- **Frontend** : HTML5, CSS3 (MOA Design System), JavaScript vanilla
- **Validation** : email-validator
- **Import/Export** : openpyxl

## 📊 Fonctionnalités Complètes

### 🔐 Authentification et Sécurité
- Système de connexion sécurisé avec Flask-Login
- Gestion des sessions utilisateur
- Hashage des mots de passe avec Werkzeug
- Suivi automatique de toutes les activités utilisateur
- Middleware de logging des actions

### 🏢 Gestion Multi-Établissements
- Support de plusieurs établissements simultanément
- Configuration individuelle par établissement (devise, taxes, etc.)
- Logo personnalisé par établissement
- Activation/désactivation des établissements
- Numérotation automatique des réservations par établissement

### 📅 Gestion des Séjours (Réservations)
- Création et modification de séjours
- Numérotation automatique et personnalisable (format: RES-{YYYY}{MM}{DD}-{NUM})
- Attribution de chambres multiples
- Gestion multi-clients par séjour
- Calcul automatique des taxes, TVA et charges plateforme
- Suivi des statuts (actif, fermé)
- Page de détail complète avec résumé financier
- Clôture de séjours avec tracking de date

### 🛏️ Gestion des Chambres
- CRUD complet des chambres
- Association aux établissements
- Définition de la capacité et du prix par nuit
- Gestion des statuts (disponible, occupée, maintenance, hors service)
- Description détaillée

### 👥 Gestion des Clients
- Base de données complète des clients
- Informations personnelles (nom, prénom, email, téléphone)
- Gestion des pièces d'identité (type et numéro)
- Date de naissance et informations de contact
- Association aux séjours
- Export Excel des listes clients
- Définition du contact principal par séjour

### 👔 Gestion du Personnel
- CRUD complet du personnel
- Informations professionnelles (poste, salaire, date d'embauche)
- Gestion granulaire des accès par section:
  - Accès dashboard
  - Accès séjours
  - Accès clients
  - Accès extras
  - Accès statistiques
  - Accès paramètres
- Activation/désactivation des comptes
- Association aux établissements

### 💰 Gestion des Extras
- Création d'extras personnalisés (services additionnels)
- Définition du prix unitaire et de l'unité
- Association aux séjours
- Calcul automatique des montants totaux
- Suivi des quantités
- Facturation intégrée aux séjours
- Gestion par établissement

### 📊 Statistiques Avancées
- Vue d'ensemble des séjours (total, actifs, fermés)
- Métriques clients (total, clients uniques)
- Performance par établissement
- Taux d'occupation des chambres
- Graphiques et visualisations en temps réel
- Tableaux de bord colorés avec design MOA

### 📝 Historique des Activités
- Suivi automatique de toutes les actions utilisateur
- Filtres avancés (type d'action, date, utilisateur)
- Affichage détaillé (route, méthode HTTP, IP, user agent)
- Export CSV des logs
- Pagination performante
- Détails JSON pour chaque action
- Interface moderne avec filtres organisés

### 📅 Calendriers iCal (Synchronisation)
- Support Airbnb, Booking.com et autres plateformes
- Synchronisation automatique des réservations externes
- Gestion multi-calendriers par établissement
- **Affichage double vue:**
  - Vue Liste: Tableau détaillé des réservations
  - Vue Calendrier: Calendrier visuel mensuel avec réservations
- Bouton de basculement entre les vues
- Statut de synchronisation en temps réel
- Import automatique des réservations externes

### 📧 Messagerie (Mail)
- Configuration de comptes email (SMTP/POP)
- Envoi et réception d'emails
- Gestion des dossiers (inbox, envoyé, etc.)
- Marquage des messages (lu/non-lu, favoris)
- Recherche par email client
- Support des pièces jointes

### ⚙️ Paramètres Système Complets
- **Informations Établissement:**
  - Nom, adresse, contact
  - Numéro d'identification
  - Logo personnalisé
  - Devise (MAD, EUR, USD, etc.)
- **Configuration Financière:**
  - Taux de taxe de séjour
  - Taux de TVA
  - Taux de charge plateforme
- **Gestion des Chambres:**
  - Nombre de chambres
  - Prix par chambre
- **Gestion des Utilisateurs:**
  - Création et modification de comptes
  - Gestion des rôles
- **Utilitaires:**
  - Export de données
  - Importation de données
  - Réinitialisation

### 📁 Export et Gestion des Données
- Export Excel des listes clients
- Export CSV des logs d'activité
- Export des statistiques
- Gestion des sauvegardes
- Import de données depuis Excel

## 🎨 Guide de style MOA

### Couleurs principales
- **Bleu** (`#3b82f6`) : Actions primaires
- **Vert** (`#22c55e`) : Succès, validations
- **Violet** (`#8b5cf6`) : Sections spéciales
- **Orange** (`#f97316`) : Avertissements
- **Rouge** (`#ef4444`) : Erreurs, suppressions

### Sections pointillées
Les sections utilisent des bordures pointillées (3px dotted) avec des couleurs correspondant à leur fonction :
```css
.section-blue { border: 3px dotted #3b82f6; }
.section-green { border: 3px dotted #22c55e; }
.section-purple { border: 3px dotted #a855f7; }
```

### Boutons
Tous les boutons utilisent des bordures solides (2px) :
```css
.btn-primary {
    background: #eff6ff;
    color: #1d4ed8;
    border: 2px solid #3b82f6;
}
```

## 🔧 Configuration

### Variables d'environnement
- `DATABASE_URL` : URL de connexion PostgreSQL
- `SECRET_KEY` : Clé secrète Flask (optionnel, défaut en développement)
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` : Configuration PostgreSQL

### Base de données

Le système crée automatiquement les tables suivantes :
- `users` : Utilisateurs du système
- `reservations` : Réservations
- `personnes` : Clients et contacts
- `parametres_systeme` : Configuration de l'établissement

## 📝 Développement

### Lancer en mode développement
```bash
flask run --debug
```

### Réinitialiser la base de données
```bash
uv run python -c "from backend.config.database import init_db; init_db()"
```

## 📄 Licence

Développé par MOA Digital Agency LLC

## 👨‍💻 Auteur

**MOA Digital Agency LLC**
- Créé par : Aisance KALONJI
- Email : moa@myoneart.com
- Website : www.myoneart.com

## 🆘 Support

Pour toute question ou problème, veuillez contacter l'équipe de support MOA.

---

**Version** : 1.0.0  
**Dernière mise à jour** : Novembre 2025
