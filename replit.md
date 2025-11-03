# Application de Gestion d'Accueil - Maison d'Hôte

## Vue d'ensemble

Application web responsive pour la gestion et l'accueil des clients d'un établissement type maison d'hôte, riad, ou hébergement touristique. L'application permet d'enregistrer les informations complètes des clients et de les gérer via une interface web moderne.

**Créé le:** 3 novembre 2025  
**Version:** 1.0.0  
**Design System:** MOA Design System

## Architecture du Projet

```
.
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py          # Configuration PostgreSQL
│   ├── models/
│   │   ├── __init__.py
│   │   └── client.py            # Modèle Client (CRUD)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── clients.py           # Routes API REST
│   ├── __init__.py
│   └── app.py                   # Application Flask principale
│
├── frontend/
│   ├── static/
│   │   └── css/
│   │       └── styles.css       # Design System MOA
│   └── templates/
│       ├── base.html            # Template de base
│       ├── index.html           # Formulaire d'accueil
│       └── clients.html         # Liste et gestion des clients
│
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

### 1. Enregistrement Client (Page d'Accueil)
Formulaire complet organisé en 4 sections :

**Section Bleue - Informations Personnelles**
- Nom (requis)
- Prénom (requis)
- Email
- Pays
- Téléphone

**Section Verte - Informations de Séjour**
- Date d'arrivée
- Date de départ
- Numéro de séjour

**Section Violette - Informations Financières**
- Facture hébergement
- Charge plate-forme
- Taxe séjour

**Section Orange - Informations Mensuelles**
- Revenu mensuel hébergement
- Charges plate-forme mensuelle
- Taxe séjour mensuelle

### 2. Gestion des Clients (Page Clients)
- Liste complète des clients enregistrés
- Tableau responsive avec toutes les informations essentielles
- Actions disponibles :
  - **Détails** : Voir toutes les informations d'un client
  - **Supprimer** : Suppression avec confirmation
- Modal pour affichage détaillé des informations client

### 3. API REST
Endpoints disponibles :
- `GET /api/clients` - Liste tous les clients
- `GET /api/clients/<id>` - Détails d'un client
- `POST /api/clients` - Créer un nouveau client
- `PUT /api/clients/<id>` - Modifier un client
- `DELETE /api/clients/<id>` - Supprimer un client

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

## Base de Données

### Table `clients`

| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL | Clé primaire auto-incrémentée |
| nom | VARCHAR(100) | Nom du client (requis) |
| prenom | VARCHAR(100) | Prénom du client (requis) |
| mail | VARCHAR(150) | Email du client |
| pays | VARCHAR(100) | Pays d'origine |
| tel | VARCHAR(50) | Numéro de téléphone |
| arrivee | DATE | Date d'arrivée |
| depart | DATE | Date de départ |
| sejour_numero | VARCHAR(50) | Numéro de séjour |
| facture_hebergement | DECIMAL(10,2) | Montant facture |
| charge_plateforme | DECIMAL(10,2) | Frais plate-forme |
| taxe_sejour | DECIMAL(10,2) | Taxe de séjour |
| revenu_mensuel_hebergement | DECIMAL(10,2) | Revenu mensuel |
| charges_plateforme_mensuelle | DECIMAL(10,2) | Charges mensuelles |
| taxe_sejour_mensuelle | DECIMAL(10,2) | Taxe mensuelle |
| created_at | TIMESTAMP | Date de création (auto) |

## Configuration et Déploiement

### Variables d'environnement
- `DATABASE_URL` : URL de connexion PostgreSQL
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` : Détails DB

### Workflow
- **Nom:** Flask App
- **Commande:** `python -m backend.app`
- **Port:** 5000
- **Type:** webview

### Lancement local
```bash
python -m backend.app
```
L'application sera accessible sur http://localhost:5000

## Sécurité et Bonnes Pratiques

- ✅ Connexions PostgreSQL sécurisées via psycopg2
- ✅ CORS configuré pour permettre les requêtes cross-origin
- ✅ Validation côté client et serveur
- ✅ Requêtes SQL paramétrées (protection SQL injection)
- ✅ Confirmations avant suppressions
- ✅ Gestion d'erreurs avec messages utilisateur

## Améliorations Futures

### Fonctionnalités
- [ ] Authentification utilisateur
- [ ] Export des données en Excel
- [ ] Recherche et filtres avancés
- [ ] Statistiques et rapports
- [ ] Gestion des chambres/réservations
- [ ] Envoi d'emails automatiques
- [ ] Historique des modifications

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

**Dernière mise à jour:** 3 novembre 2025
