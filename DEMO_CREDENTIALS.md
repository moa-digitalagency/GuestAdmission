# 🏨 Système de Gestion Hôtelière - Données de Démonstration

## 📊 Résumé des Données Créées

L'application contient maintenant des données de démonstration complètes :

- **3 Comptes Tenants** (groupes hôteliers)
- **5 Établissements** (hôtels et riads)
- **27 Chambres** (différents types et capacités)
- **56 Réservations** (passées, en cours, futures)
- **146 Clients** (de différents pays)
- **19 Extras** (services additionnels)

## 🔐 Identifiants de Connexion

### Platform Admin (Super Administrateur)
- **Username:** `admin`
- **Password:** `admin123`
- **Accès:** Gestion complète de la plateforme, tous les tenants et établissements

### Tenant Admins (Administrateurs de Groupes)

**Tenant 1 - Groupe Hôtelier Atlas**
- **Username:** `admin1`
- **Password:** `demo123`
- **Établissements:** Riad Marrakech Excellence, Hotel Casablanca Premium

**Tenant 2 - Riads & Maisons d'Hôtes du Maroc**
- **Username:** `admin2`
- **Password:** `demo123`
- **Établissements:** Riad Essaouira Charm, Dar Fes Authentique

**Tenant 3 - Hospitality Partners**
- **Username:** `admin3`
- **Password:** `demo123`
- **Établissements:** Villa Agadir Ocean View

## 🏨 Établissements Créés

### 1. Riad Marrakech Excellence
- **Localisation:** 45 Derb Sidi Ahmed Soussi, Medina, Marrakech
- **Contact:** +212 524 123 456 | contact@riadmarrakech.com
- **Chambres:** 5 chambres
- **Type:** Riad traditionnel

### 2. Hotel Casablanca Premium
- **Localisation:** 123 Boulevard Ain Diab, Casablanca
- **Contact:** +212 522 987 654 | info@casablancahotel.ma
- **Chambres:** 6 chambres
- **Type:** Hôtel moderne

### 3. Riad Essaouira Charm
- **Localisation:** 78 Rue de la Skala, Essaouira
- **Contact:** +212 524 555 777 | hello@essaouirariad.com
- **Chambres:** 5 chambres
- **Type:** Riad côtier

### 4. Dar Fes Authentique
- **Localisation:** 12 Derb Talaa Kebira, Fes El Bali, Fes
- **Contact:** +212 535 111 222 | contact@darfes.ma
- **Chambres:** 5 chambres
- **Type:** Maison d'hôtes traditionnelle

### 5. Villa Agadir Ocean View
- **Localisation:** Boulevard du 20 Août, Agadir
- **Contact:** +212 528 333 444 | info@villaagadir.com
- **Chambres:** 6 chambres
- **Type:** Villa moderne avec vue mer

## 🎯 Fonctionnalités à Tester

### Tableau de Bord Platform Admin
1. **Statistiques globales** : Vue d'ensemble de tous les tenants
2. **Gestion des comptes clients** : Créer, modifier, désactiver des tenants
3. **Gestion des établissements** : Vue de tous les établissements
4. **Gestion des utilisateurs** : Administration des accès
5. **Paramètres de la plateforme** : Configuration générale

### Tableau de Bord Tenant Admin
1. **Dashboard** : Statistiques de vos établissements
2. **Séjours** : Gestion des réservations
3. **Clients** : Base de données clients
4. **Chambres** : Inventaire et tarifs
5. **Extras** : Services additionnels
6. **Statistiques** : Rapports et analyses
7. **Messagerie** : Communication
8. **Calendriers** : Synchronisation iCal

## 🚀 Comment Utiliser

1. **Connectez-vous** avec l'un des identifiants ci-dessus
2. **Explorez le dashboard** pour voir les statistiques
3. **Naviguez** entre les différentes sections via le menu latéral
4. **Testez les fonctionnalités** :
   - Créer une nouvelle réservation
   - Ajouter un client
   - Gérer les chambres
   - Voir les statistiques
   - Configurer les extras

## 📝 Notes Importantes

- Toutes les données sont fictives et à des fins de démonstration uniquement
- Les réservations incluent des dates passées, présentes et futures
- Les clients proviennent de différents pays pour tester l'internationalisation
- Les prix sont en MAD (Dirham marocain)

## 🔄 Réinitialisation des Données

Pour recharger les données de démonstration :
```bash
python create_demo_data.py
```

Pour initialiser une base vide :
```bash
python init_database.py
```
