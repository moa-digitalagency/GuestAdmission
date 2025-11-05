# 📚 Documentation du Projet

Ce dossier contient toute la documentation technique du système de gestion SaaS multi-tenant.

## 📁 Structure de la documentation

### Transformation SaaS
- **[TRANSFORMATION_SAAS_COMPLETE.md](TRANSFORMATION_SAAS_COMPLETE.md)** - Guide complet de la transformation SaaS avec résumé des fonctionnalités
- **[SAAS_MIGRATION_GUIDE.md](SAAS_MIGRATION_GUIDE.md)** - Guide détaillé de migration vers l'architecture SaaS
- **[TEST_SAAS_IMPLEMENTATION.md](TEST_SAAS_IMPLEMENTATION.md)** - Tests et validation de l'implémentation SaaS

### Guides techniques
- **[DEPLOYMENT_NOTES.md](DEPLOYMENT_NOTES.md)** - Notes pour le déploiement en production
- **[STYLE_GUIDE.md](STYLE_GUIDE.md)** - Guide de style pour le développement

## 🔗 Liens rapides

### Architecture SaaS
Le système utilise une architecture multi-tenant avec 3 niveaux de rôles :
1. **PLATFORM_ADMIN** - Gestion de la plateforme SaaS
2. **Tenant Admin** - Gestion des établissements d'un compte client
3. **Utilisateur** - Accès limité aux établissements assignés

### Identifiants de démonstration
- Platform Admin : `admin / admin123`
- Riad Atlas Admin : `riad_admin / riad123`
- Villa Ocean Admin : `villa_admin / villa123`

### Dashboards
- Platform Admin : `/platform-admin`
- Tenant Admin : `/tenant`
- Utilisateur régulier : `/dashboard`

## 📖 Documentation du code source

Le fichier **[../replit.md](../replit.md)** à la racine contient :
- Vue d'ensemble du projet
- Changements récents
- Préférences utilisateur
- Architecture système détaillée

---

*Pour plus d'informations, consultez le README principal à la racine du projet.*
