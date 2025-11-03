# Système de Gestion de Réservations - Maison d'Hôte

## Vue d'ensemble

Système complet de gestion de réservations pour établissements touristiques (maisons d'hôte, riads, etc.). L'application offre un système d'authentification, la gestion multi-personnes par réservation, le calcul automatique de la durée de séjour, et une interface moderne avec navigation latérale.

**Créé le:** 3 novembre 2025  
**Version:** 2.1.0  
**Design System:** MOA Design System  
**Authentification:** Flask-Login  
**Initialisation:** Automatique à chaque déploiement

## Architecture du Projet

```
.
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py          # Configuration PostgreSQL
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py            # Modèle Client
│   │   ├── user.py              # Modèle Utilisateur
│   │   ├── reservation.py       # Modèle Réservation
│   │   └── personne.py          # Modèle Personne
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Routes authentification
│   │   ├── clients.py           # Routes API clients
│   │   ├── reservations.py      # Routes API réservations
│   │   ├── parametres.py        # Routes API paramètres
│   │   └── countries.py         # Routes API pays
│   ├── __init__.py
│   └── app.py                   # Application Flask principale
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css       # Design System MOA
│   │   └── data/
│   │       └── countries.json   # Données pays et villes
│   └── templates/
│       ├── base_dashboard.html  # Template dashboard avec sidebar
│       ├── login.html           # Page de connexion
│       ├── dashboard.html       # Tableau de bord
│       ├── nouvelle_reservation.html
│       ├── reservations.html
│       ├── clients_list.html
│       └── parametres.html      # Page paramètres système
│
├── init_database.py             # Script d'initialisation DB
├── main.py                      # Point d'entrée principal
└── attached_assets/
    ├── Dowaya Fichier Clients_*.xlsx
    └── moa-design-system-style_*.json
```

## Stack Technique

### Backend
- **Framework:** Flask (Python 3.11)
- **Base de données:** PostgreSQL (Replit Managed)
- **CORS:** Flask-CORS
- **Driver DB:** psycopg2-binary

### Frontend
- **HTML5** avec templates Jinja2
- **CSS3** personnalisé selon MOA Design System
- **JavaScript** vanilla pour interactions
- **Responsive Design:** Mobile, Tablette, PC

## Fonctionnalités

### 1. Système d'Authentification
- **Page de login sécurisée** avec design moderne (fond dégradé violet)
- Compte admin par défaut : `admin` / `admin123`
- Protection de toutes les pages avec Flask-Login
- Déconnexion sécurisée
- Gestion de sessions utilisateur

### 2. Tableau de Bord
- **Statistiques en temps réel** :
  - Réservations actives
  - Total clients
  - Arrivées du jour
  - Revenus du mois
- Liste des réservations récentes
- Navigation rapide vers les fonctions principales

### 3. Nouvelle Réservation (Multi-personnes)
**Section Verte - Informations de Séjour**
- Date d'arrivée et date de départ
- **Calcul automatique du nombre de jours** de séjour
- Numéro de séjour

**Section Violette - Informations Financières**
- Facture hébergement
- Charge plate-forme
- Taxe séjour

**Section Bleue - Gestion Multi-Personnes**
- Ajout illimité de personnes (voyageurs)
- Première personne = **contact principal** de la réservation
- Pour chaque personne :
  - Nom et prénom (requis)
  - Email, téléphone, pays
  - **Type de pièce d'identité** : Passeport ou CIN
  - Numéro de pièce d'identité
  - Date de naissance
- Interface intuitive avec cartes distinctives
- Suppression possible (sauf contact principal)

### 4. Gestion des Réservations
- Liste complète des réservations avec contact principal
- Affichage : dates, durée, facture, statut
- Modal de détails complet avec :
  - Informations de séjour
  - Informations financières
  - Liste de toutes les personnes liées
- Suppression avec confirmation

### 5. Base de Données Clients
- Vue complète de toutes les personnes enregistrées
- Informations affichées :
  - Identité complète
  - Coordonnées
  - Pièce d'identité (type et numéro)
  - Statut (contact principal ou non)

### 6. Paramètres Système
- Configuration de l'établissement
- Informations du compte utilisateur
- Statistiques globales (réservations, clients)

### 7. Navigation Latérale (Sidebar)
- **Design professionnel** avec bordure pointillée bleue (MOA)
- **Alignement à gauche** avec bords arrondis au hover
- **Logo 🏡** dans l'en-tête
- Menu fixe avec icônes :
  - 📊 Tableau de bord
  - ➕ Nouvelle réservation
  - 📅 Réservations
  - 👥 Base clients
  - ⚙️ Paramètres
  - 🚪 Déconnexion
- Effet de survol moderne avec ombre bleue
- Indicateur visuel de la page active
- Responsive (adapté mobile/tablette/PC)

### 8. API REST Complète
**Authentification**
- `GET /login` - Page de connexion
- `POST /login` - Authentifier un utilisateur
- `GET /logout` - Déconnexion
- `GET /api/current-user` - Info utilisateur connecté

**Réservations**
- `GET /api/reservations` - Liste toutes les réservations
- `GET /api/reservations/<id>` - Détails d'une réservation
- `POST /api/reservations` - Créer réservation + personnes
- `PUT /api/reservations/<id>` - Modifier une réservation
- `DELETE /api/reservations/<id>` - Supprimer une réservation

**Personnes**
- `GET /api/personnes` - Liste tous les clients
- `POST /api/personnes` - Ajouter une personne
- `PUT /api/personnes/<id>` - Modifier une personne
- `DELETE /api/personnes/<id>` - Supprimer une personne

## Design System MOA

L'application utilise le **MOA Design System** avec :

### Caractéristiques principales
- **Sections pointillées colorées** : Bordures dotted de 3px
- **Palette de couleurs** : Bleu (primaire), Vert (succès), Violet/Orange (sections)
- **Boutons modernes** : Avec ombres et transitions
- **Typography compacte** : Police system-ui optimisée
- **Responsive mobile-first**

### Composants spécifiques
- Navigation avec bordure pointillée bleue
- Formulaires avec grille responsive
- Badges colorés pour statuts
- Modals avec animations
- Alertes de confirmation

## Base de Données (Nouvelle Architecture)

### Table `users` - Utilisateurs administrateurs
| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Clé primaire |
| username | VARCHAR(100) | Nom d'utilisateur (unique) |
| password_hash | VARCHAR(255) | Mot de passe hashé (sécurisé) |
| nom | VARCHAR(100) | Nom de l'utilisateur |
| prenom | VARCHAR(100) | Prénom de l'utilisateur |
| email | VARCHAR(150) | Email |
| role | VARCHAR(50) | Rôle (admin par défaut) |
| created_at | TIMESTAMP | Date de création |

**Compte par défaut** : username=`admin`, password=`admin123`

### Table `reservations` - Réservations
| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Clé primaire |
| date_arrivee | DATE | Date d'arrivée (requis) |
| date_depart | DATE | Date de départ (requis) |
| nombre_jours | INTEGER | Nombre de jours (calculé auto) |
| sejour_numero | VARCHAR(50) | Numéro de séjour |
| facture_hebergement | DECIMAL(10,2) | Facture hébergement |
| charge_plateforme | DECIMAL(10,2) | Charge plate-forme |
| taxe_sejour | DECIMAL(10,2) | Taxe de séjour |
| revenu_mensuel_hebergement | DECIMAL(10,2) | Revenu mensuel |
| charges_plateforme_mensuelle | DECIMAL(10,2) | Charges mensuelles |
| taxe_sejour_mensuelle | DECIMAL(10,2) | Taxe mensuelle |
| statut | VARCHAR(50) | Statut (active, terminée, etc.) |
| notes | TEXT | Notes libres |
| created_at | TIMESTAMP | Date de création |
| updated_at | TIMESTAMP | Date de modification |

### Table `personnes` - Personnes liées aux réservations
| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Clé primaire |
| reservation_id | INTEGER | FK vers reservations (CASCADE) |
| est_contact_principal | BOOLEAN | Contact principal de la réservation |
| nom | VARCHAR(100) | Nom (requis) |
| prenom | VARCHAR(100) | Prénom (requis) |
| email | VARCHAR(150) | Email |
| telephone | VARCHAR(50) | Téléphone |
| pays | VARCHAR(100) | Pays |
| **type_piece_identite** | VARCHAR(50) | Type : **passeport** ou **cin** |
| **numero_piece_identite** | VARCHAR(100) | Numéro de la pièce |
| date_naissance | DATE | Date de naissance |
| created_at | TIMESTAMP | Date de création |

**Relation** : Une réservation peut avoir plusieurs personnes, la première est le contact principal.

### Table `parametres_systeme` - Configuration système
| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Clé primaire |
| nom_etablissement | VARCHAR(200) | Nom de l'établissement |
| **pays** | VARCHAR(100) | **Pays de l'établissement** |
| adresse | TEXT | Adresse |
| telephone | VARCHAR(50) | Téléphone |
| email | VARCHAR(150) | Email |
| devise | VARCHAR(10) | Devise (MAD par défaut) |
| taux_taxe_sejour | DECIMAL(5,2) | Taux taxe séjour (%) |
| **taux_tva** | DECIMAL(5,2) | **Taux TVA (%)** |
| taux_charge_plateforme | DECIMAL(5,2) | Taux charge plate-forme (%) |
| **nombre_chambres** | INTEGER | **Nombre de chambres** |
| **prix_chambres** | JSONB | **Prix par chambre (tableau)** |
| logo_url | VARCHAR(500) | URL du logo |
| created_at | TIMESTAMP | Date de création |
| updated_at | TIMESTAMP | Date de modification |

## Configuration et Déploiement

### Variables d'environnement
- `DATABASE_URL` : URL de connexion PostgreSQL (requis)
- `SESSION_SECRET` : Clé secrète pour les sessions Flask
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` : Détails DB

### Initialisation automatique de la base de données
L'application utilise un **script d'initialisation automatique** (`init_database.py`) qui :
- ✅ Crée toutes les tables nécessaires si elles n'existent pas
- ✅ Crée l'utilisateur admin par défaut (admin/admin123)
- ✅ Initialise les paramètres système avec valeurs par défaut
- ✅ S'exécute automatiquement à chaque déploiement
- ✅ Est idempotent (peut être exécuté plusieurs fois sans problème)

### Workflow
- **Nom:** Flask App
- **Commande:** `python init_database.py && uv run gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`
- **Port:** 5000
- **Type:** webview
- **Ordre d'exécution:**
  1. Initialisation de la base de données
  2. Démarrage de Gunicorn avec l'application Flask

### Lancement local
```bash
# Initialiser la base de données
python init_database.py

# Démarrer l'application
python main.py
```
L'application sera accessible sur http://localhost:5000

## Sécurité et Bonnes Pratiques

- ✅ Connexions PostgreSQL sécurisées via psycopg2
- ✅ CORS configuré pour permettre les requêtes cross-origin
- ✅ Validation côté client et serveur
- ✅ Requêtes SQL paramétrées (protection SQL injection)
- ✅ Confirmations avant suppressions
- ✅ Gestion d'erreurs avec messages utilisateur

## Améliorations Réalisées

### Version 2.1.0 (3 novembre 2025)
- ✅ **Initialisation automatique de la DB** à chaque déploiement
- ✅ **Script init_database.py** robuste et idempotent
- ✅ **Sidebar améliorée** : alignement à gauche, bords arrondis au hover
- ✅ **Liste de devises sélectionnables** (12 devises disponibles)
- ✅ **Gestion de plusieurs responsables** dans les paramètres
- ✅ **Parsing JSON correct** pour les champs JSONB (responsables, prix_chambres)

### Version 2.0.0 (3 novembre 2025)
- ✅ **Authentification admin sécurisée** avec Flask-Login
- ✅ **Gestion multi-personnes** par réservation
- ✅ **Pièces d'identité** (Passeport/CIN) pour chaque personne
- ✅ **Calcul automatique** du nombre de jours de séjour
- ✅ **Navigation latérale** professionnelle et responsive
- ✅ **Nouvelle architecture de base de données** (users, reservations, personnes, parametres)
- ✅ **Tableau de bord** avec statistiques en temps réel
- ✅ **Contact principal** distinct pour chaque réservation

## Améliorations Futures

### Fonctionnalités
- [ ] Export des données en Excel
- [ ] Recherche et filtres avancés dans les réservations
- [ ] Statistiques et rapports détaillés
- [ ] Gestion des chambres et disponibilité
- [ ] Envoi d'emails automatiques (confirmations, rappels)
- [ ] Historique des modifications
- [ ] Import de données Excel existantes
- [ ] Gestion multi-utilisateurs avec rôles

### Technique
- [ ] Tests unitaires et d'intégration
- [ ] Cache Redis pour performances
- [ ] API documentation (Swagger)
- [ ] Pagination pour grandes listes
- [ ] Backup automatique de la base

## Notes de Développement

- La structure est modulaire et extensible
- Le design MOA est appliqué de manière cohérente
- Les fichiers Excel peuvent être importés ultérieurement
- L'application est prête pour le déploiement en production

## Contact et Support

Pour toute question ou amélioration, contactez l'équipe de développement.

---

**Dernière mise à jour:** 3 novembre 2025 (Page paramètres améliorée)
