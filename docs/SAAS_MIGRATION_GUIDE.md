# Guide de Migration SaaS - Maison d'Hôte

Ce document décrit la transformation de l'application en un système SaaS multi-tenant complet.

## Vue d'ensemble de la transformation

L'application a été transformée d'un système mono-tenant en une plateforme SaaS complète avec trois niveaux de hiérarchie:

### Nouvelle hiérarchie des rôles

1. **PLATFORM_ADMIN** (Niveau le plus élevé)
   - Admin de la plateforme SaaS
   - Crée et gère les comptes clients (tenants)
   - Accès à toutes les statistiques globales
   - Dashboard séparé: `/platform-admin`

2. **admin** (Tenant Admin)
   - Admin d'un compte client (tenant)
   - Peut gérer plusieurs établissements sous son compte
   - Peut ajouter des établissements supplémentaires
   - Peut ajouter et gérer des utilisateurs
   - Dashboard tenant: `/tenant` ou `/dashboard`

3. **Utilisateurs réguliers**
   - Accès limité aux établissements assignés

## Architecture SaaS

### Nouveaux modèles de données

#### TenantAccount (Compte Client)
```python
- id: Identifiant unique
- nom_compte: Nom du compte client
- primary_admin_user_id: Admin principal du compte
- date_creation: Date de création
- actif: Statut actif/inactif
- notes: Notes sur le compte
```

#### Modifications des modèles existants

**Etablissement**:
- Ajout de `tenant_account_id` pour lier à un compte tenant
- Plusieurs établissements peuvent appartenir au même tenant

**User**:
- Nouvelles méthodes: `is_platform_admin()`, `get_tenant_account_id()`
- Support du rôle PLATFORM_ADMIN

**UserEtablissements**:
- Ajout de `is_primary_admin` pour identifier l'admin principal

### Nouveaux endpoints API

#### Platform Admin (PLATFORM_ADMIN seulement)

**Gestion des tenants:**
- `GET /api/platform-admin/tenants` - Liste des comptes clients
- `POST /api/platform-admin/tenants` - Créer un compte client avec établissement et admin
- `GET /api/platform-admin/tenants/<id>` - Détails d'un tenant
- `PUT /api/platform-admin/tenants/<id>` - Mettre à jour un tenant
- `DELETE /api/platform-admin/tenants/<id>` - Désactiver un tenant

**Statistiques:**
- `GET /api/platform-admin/stats` - Statistiques globales de la plateforme

**Utilisateurs:**
- `GET /api/platform-admin/users` - Liste de tous les utilisateurs
- `DELETE /api/platform-admin/users/<id>` - Supprimer un utilisateur

#### Tenant Admin (admin seulement)

**Établissements:**
- `GET /api/tenant/etablissements` - Mes établissements
- `POST /api/tenant/etablissements` - Ajouter un établissement à mon compte
- `PUT /api/tenant/etablissements/<id>` - Mettre à jour un établissement
- `DELETE /api/tenant/etablissements/<id>` - Supprimer un établissement

**Chambres:**
- `GET /api/tenant/etablissements/<id>/chambres` - Chambres d'un établissement
- `POST /api/tenant/etablissements/<id>/chambres` - Ajouter une chambre

**Utilisateurs:**
- `GET /api/tenant/users` - Utilisateurs de mon compte
- `POST /api/tenant/users` - Ajouter un utilisateur
- `DELETE /api/tenant/users/<id>` - Retirer un utilisateur

**Statistiques:**
- `GET /api/tenant/stats` - Statistiques de mon compte

## Migration de la base de données

### Migration 004: Transformation SaaS

**Exécution:**
```bash
python3 migrations/004_add_platform_admin_role.py
```

**Modifications:**
1. Création de la table `tenant_accounts`
2. Ajout de `tenant_account_id` dans `etablissements`
3. Transformation de `SUPER_ADMIN` en `PLATFORM_ADMIN`
4. Ajout de `is_primary_admin` dans `user_etablissements`

**Important**: Cette migration transforme automatiquement les utilisateurs SUPER_ADMIN existants en PLATFORM_ADMIN.

## Nouveaux Dashboards

### Platform Admin Dashboard (`/platform-admin`)

**Fonctionnalités:**
- Vue d'ensemble avec statistiques globales
- Gestion des comptes clients (tenants)
- Vue de tous les établissements
- Gestion de tous les utilisateurs
- Création de nouveaux comptes clients avec:
  - Informations du compte
  - Premier établissement
  - Admin principal

**Navigation:**
- Tableau de bord
- Comptes clients
- Établissements
- Utilisateurs

### Tenant Dashboard (`/tenant`)

**Fonctionnalités:**
- Statistiques du compte (établissements, chambres, réservations, utilisateurs)
- Liste des établissements du compte
- Ajouter des établissements supplémentaires
- Gérer les utilisateurs du compte
- Ajouter des utilisateurs avec accès multi-établissements

## Flux de travail

### Création d'un nouveau compte client (Platform Admin)

1. Le PLATFORM_ADMIN accède à `/platform-admin`
2. Clique sur "Créer un compte client"
3. Remplit:
   - Nom du compte client
   - Informations du premier établissement
   - Identifiants de l'admin principal
4. Le système crée:
   - Le compte tenant
   - L'établissement (lié au tenant)
   - L'utilisateur admin principal
   - L'association user-établissement avec flag `is_primary_admin`

### Admin tenant ajoute un établissement

1. L'admin se connecte et accède à `/tenant`
2. Clique sur "Ajouter un établissement"
3. Remplit les informations de l'établissement
4. L'établissement est automatiquement lié au même `tenant_account_id`
5. L'admin est automatiquement ajouté à cet établissement

### Admin tenant ajoute un utilisateur

1. Dans `/tenant`, clic sur "Gérer les utilisateurs"
2. Clique sur "Ajouter un utilisateur"
3. Remplit les informations et sélectionne les établissements (multiple)
4. L'utilisateur est créé avec accès aux établissements sélectionnés
5. L'utilisateur appartient automatiquement au même tenant_account

## Sécurité et isolation

### Isolation des tenants

- Chaque tenant ne voit que ses propres données
- Les requêtes sont filtrées par `tenant_account_id`
- Les admins ne peuvent pas accéder aux données d'autres tenants
- PLATFORM_ADMIN a vue globale mais accès en lecture principalement

### Décorateurs de sécurité

```python
@platform_admin_required  # PLATFORM_ADMIN uniquement
@tenant_admin_required    # admin (tenant) uniquement
@super_admin_required     # Alias pour compatibilité
```

### Validation des accès

- Toutes les routes tenant vérifient `can_manage_etablissement()`
- Les utilisateurs ne peuvent gérer que les établissements de leur tenant
- PLATFORM_ADMIN a accès complet mais via routes séparées

## Compatibilité

### Routes de compatibilité

- `/super-admin` redirige vers `/platform-admin`
- `is_super_admin()` retourne True pour PLATFORM_ADMIN
- Les anciennes routes super_admin continuent de fonctionner

### Migration progressive

1. Les utilisateurs SUPER_ADMIN existants deviennent PLATFORM_ADMIN
2. Les admins existants conservent leur rôle
3. Aucune perte de données
4. Les établissements existants peuvent être regroupés en tenants

## Prochaines étapes

### Pour déployer:

**IMPORTANT**: Cette migration nécessite que la base de données existe et que toutes les migrations précédentes aient été exécutées.

**Prérequis:**
1. Base de données PostgreSQL créée et accessible via DATABASE_URL
2. Toutes les migrations précédentes exécutées (001, 002, 003)
3. Tables de base existantes: users, etablissements, chambres, reservations, etc.

**Étapes de déploiement:**

1. **Vérifier que la base de données existe**
   ```bash
   # Si la base n'existe pas, créer via Replit UI ou:
   # Exécuter init_database.py pour créer les tables de base
   python3 init_database.py
   ```

2. **Exécuter les migrations précédentes si nécessaire**
   ```bash
   # Si pas déjà fait
   python3 migrations/001_add_sejour_closure_tracking.py
   python3 migrations/002_add_multi_tenant_support.py
   python3 migrations/003_fix_user_etablissement_associations.py
   ```

3. **Backup de la base de données**
   ```bash
   # Créer un backup avant migration
   pg_dump $DATABASE_URL > backup_avant_saas.sql
   ```

4. **Exécuter la migration SaaS**
   ```bash
   python3 migrations/004_add_platform_admin_role.py
   ```

3. **Vérifier les utilisateurs**
   - Se connecter avec l'ancien admin (maintenant PLATFORM_ADMIN)
   - Vérifier l'accès au dashboard platform

4. **Créer le premier compte tenant (si migration d'anciens établissements)**
   - Via le dashboard platform admin
   - Ou via script de migration des données existantes

5. **Tester l'isolation**
   - Créer un second compte tenant
   - Vérifier qu'ils ne voient pas les données l'un de l'autre

### Améliorations futures

- [ ] Ajouter des métriques d'utilisation par tenant
- [ ] Système de facturation basé sur l'utilisation
- [ ] Personnalisation par tenant (logo, couleurs)
- [ ] Limites configurables par plan (nombre d'établissements, utilisateurs)
- [ ] API publique pour les tenants
- [ ] Webhooks pour les événements
- [ ] Rapports et exports au niveau tenant et plateforme

## Support

Pour toute question sur la migration:
- Consulter la documentation technique dans le code
- Vérifier les tests d'intégration
- Examiner les logs de migration

## Rollback

En cas de problème, restaurer depuis le backup:
```bash
psql $DATABASE_URL < backup_avant_saas.sql
```

**Note**: Un rollback annulera toutes les données créées après la migration.
