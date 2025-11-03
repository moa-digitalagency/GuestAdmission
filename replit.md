# Maison d'Hôte - Système de Gestion

## Vue d'ensemble
Application Flask de gestion de maison d'hôte avec gestion complète des établissements, réservations, et clients.

## État du projet - 3 novembre 2025

### ✅ Dernières mises à jour (3 nov 2025 - 22:15)
- **✨ Refactorisation Architecture - Services & Utilitaires**:
  - Création dossier `backend/services/` pour la logique métier
  - Création dossier `backend/utils/` pour les utilitaires
  - Service `SejourService` pour gestion centralisée des séjours
  - Service `ExtraService` pour gestion des suppléments
  - Séparation claire: Routes → Services → Modèles

- **💰 Système de Gestion des Extras (NOUVEAU)**:
  - Table `extras` créée avec gestion complète
  - Table `sejours_extras` pour liaison séjour-extra
  - Routes API complètes: `/api/extras` (CRUD complet)
  - Page dédiée `/extras` avec:
    - Liste des extras par établissement
    - Ajout/modification/suppression d'extras
    - Sommation des extras par période
    - Prix unitaire et unité de mesure personnalisables
  - Facturation des extras aux séjours
  - Calcul automatique du montant total

- **🎨 Amélioration Interface Séjours**:
  - Codes couleur pour les statuts:
    - ✅ Vert: Séjours actifs
    - ⚪ Gris: Séjours terminés
    - ❌ Rouge: Séjours annulés
  - Système de filtres avancés:
    - Filtrage par établissement
    - Filtrage par statut (actif/terminé/annulé)
    - Recherche par numéro de séjour ou nom contact
    - Filtrage par dates (arrivée/départ)
    - Bouton réinitialiser les filtres
  - Fonction d'impression de la liste filtrée
  - Interface en cartes au lieu de tableau

- **📄 Page Détail Séjour (NOUVELLE)**:
  - Route `/sejour/<id>` pour accès direct
  - Affichage complet des informations:
    - Informations générales du séjour
    - Détails de l'établissement
    - Chambres assignées
    - Liste des personnes/clients
    - Extras facturés avec montants
    - Récapitulatif financier total
  - Ajout d'extras directement au séjour
  - Suppression d'extras du séjour
  - Fonction d'impression optimisée pour PDF

### ✅ Dernières mises à jour (3 nov 2025 - 20:30)
- **✨ Gestion des chambres entièrement fonctionnelle**:
  - Ajout endpoint GET `/api/chambres/<id>` pour récupérer une chambre
  - Modal d'ajout/modification avec sélection d'établissement
  - Suppression et édition des chambres
  - Interface complète dans la page Paramètres

- **✨ Système de gestion du personnel créé de zéro**:
  - Table `personnels` créée avec tous les champs nécessaires
  - Routes API complètes: GET, POST, PUT, DELETE (`backend/routes/personnels.py`)
  - Interface de gestion dans Paramètres avec:
    - Ajout/modification/suppression de personnels
    - Gestion des accès par page (dashboard, séjours, clients, etc.)
    - Activation/désactivation des comptes
    - Suivi des informations professionnelles (poste, salaire, date embauche)

- **🔧 Corrections et améliorations**:
  - Tous les boutons de la page Paramètres fonctionnent maintenant
  - Application redémarrée avec toutes les nouvelles routes
  - Migration d'importation complétée

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
- **Services** (NOUVEAU):
  - `sejour_service.py` - Logique métier des séjours avec filtres
  - `extra_service.py` - Logique métier des extras et facturation
- **Utilitaires** (NOUVEAU):
  - `serializers.py` - Sérialisation des données
  - `formatters.py` - Formatage des devises, dates, numéros
- **Routes**:
  - `auth.py` - Authentification et gestion utilisateurs
  - `etablissements.py` - Gestion des établissements (CRUD complet)
  - `chambres.py` - Gestion des chambres (CRUD complet + endpoint GET single)
  - `sejours.py` - Gestion des séjours et clients (anciennement reservations.py)
  - `extras.py` - **NOUVEAU** Gestion des extras (CRUD complet + facturation)
  - `parametres.py` - Paramètres système
  - `personnels.py` - Gestion du personnel (CRUD complet)
  - `data_management.py` - Chargement demo et réinitialisation
  - `clients.py` - Gestion des clients
  - `countries.py` - API pour les pays et villes

#### Frontend
- **Templates**: `frontend/templates/`
  - `base_dashboard.html` - Template de base avec sidebar et navigation (+ lien Extras)
  - `login.html` - Page de connexion
  - `dashboard.html` - Tableau de bord
  - `statistiques.html` - Page statistiques dédiée
  - `parametres.html` - Page paramètres (Établissements, Chambres, Personnels)
  - `nouveau_sejour.html` - Créer un séjour (anciennement nouvelle_reservation.html)
  - `sejours.html` - **AMÉLIORÉ** Liste avec filtres, couleurs et impression
  - `sejour_detail.html` - **NOUVEAU** Page détail complet d'un séjour
  - `extras.html` - **NOUVEAU** Gestion des extras et sommaire
  - `clients_list.html` - Liste des clients

- **Static**: `frontend/static/`
  - `css/styles.css` - Styles CSS avec sections dotted
  - `data/countries.json` - Liste des pays et villes
  - `js/sejours.js` - **AMÉLIORÉ** Filtres, couleurs et impression
  - `js/extras.js` - **NOUVEAU** Gestion des extras
  - `js/common.js`, `js/dashboard.js`, etc. - Scripts existants

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

4. **Gestion des chambres** (NOUVEAU - Pleinement fonctionnel)
   - Création de chambres avec établissement associé
   - Modification des informations (nom, capacité, prix, statut)
   - Suppression de chambres
   - Statuts: disponible, occupée, maintenance, hors service

5. **Gestion du personnel** (NOUVEAU - Pleinement fonctionnel)
   - Création de fiches personnel
   - Informations personnelles (prénom, nom, email, téléphone)
   - Informations professionnelles (poste, salaire, date d'embauche)
   - Gestion des accès par page (permissions granulaires)
   - Activation/désactivation des comptes
   - Association à un établissement

6. **Paramètres système**
   - Gestion multi-établissements
   - Gestion chambres (nouvelle interface complète)
   - Gestion personnels (nouvelle interface complète)
   - Compte utilisateur
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
