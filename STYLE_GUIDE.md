# 🎨 Guide de Style - Maison d'Hôte

## Vue d'ensemble
Ce document définit les règles de style pour garantir une cohérence visuelle dans toute l'application.

## 🎯 Principes de Design

### Bordures Pointillées
**TOUJOURS** utiliser des bordures pointillées (dotted) de 3px pour :
- Sections principales
- Modales/Formulaires
- Blocs d'information
- Zones de contenu

### Palette de Couleurs

| Couleur | Code | Usage |
|---------|------|-------|
| Bleu | `#3b82f6` | Boutons principaux, sections |
| Violet | `#8b5cf6` | Login, sections importantes |
| Vert | `#22c55e` | Succès, validation |
| Orange | `#f97316` | Alertes, actions secondaires |
| Cyan | `#06b6d4` | Information |
| Indigo | `#6366f1` | Alternative |

## 📦 Classes CSS Réutilisables

### Sections Pointillées

```css
.dotted-section {
    border-radius: 1rem;
    padding: 1.5rem;
    transition: all 0.3s ease;
    margin-bottom: 1.5rem;
}

.section-blue {
    background: rgba(59, 130, 246, 0.05);
    border: 3px dotted #3b82f6;
    box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
}

.section-purple {
    background: rgba(139, 92, 246, 0.05);
    border: 3px dotted #8b5cf6;
    box-shadow: 0 4px 6px rgba(139, 92, 246, 0.1);
}
```

### Boutons avec Contours

```css
/* Bouton Principal (Bleu) */
.btn-primary {
    padding: 0.75rem 1.5rem;
    background: #eff6ff;
    color: #1d4ed8;
    border: 2px solid #3b82f6;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.15);
}

.btn-primary:hover {
    background: #dbeafe;
    border-color: #2563eb;
    box-shadow: 0 6px 10px rgba(59, 130, 246, 0.3);
    transform: translateY(-2px);
}

/* Bouton Secondaire (Gris) */
.btn-secondary {
    padding: 0.75rem 1.5rem;
    background: #f9fafb;
    color: #374151;
    border: 2px solid #d1d5db;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-secondary:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
}
```

### Modales/Formulaires

```css
.modal-content-dotted {
    background: white;
    border-radius: 1rem;
    border: 3px dotted #8b5cf6;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    padding: 2rem;
}

.form-group {
    margin-bottom: 1.25rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #374151;
    font-weight: 600;
    font-size: 0.875rem;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 0.625rem 0.875rem;
    border: 2px solid #d1d5db;
    border-radius: 0.5rem;
    font-size: 0.95rem;
    transition: all 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
```

## 🔲 Blocs d'Information

Pour les blocs d'information (comme "Identifiants par défaut") :

```css
.info-box {
    margin-top: 1.5rem;
    text-align: center;
    padding: 1rem;
    background: rgba(139, 92, 246, 0.08);
    border-radius: 1rem;
    border: 3px dotted #8b5cf6;
}
```

## ✅ Checklist pour Nouveaux Composants

Avant d'ajouter un nouveau formulaire/modale :
- [ ] Utiliser des bordures pointillées (3px dotted)
- [ ] Appliquer border-radius de 1rem
- [ ] Utiliser les classes de boutons `.btn-primary` ou `.btn-secondary`
- [ ] Ajouter des ombres légères (`box-shadow`)
- [ ] Inclure des transitions pour les interactions hover
- [ ] Utiliser les couleurs de la palette définie
- [ ] Ajouter des animations subtiles si approprié

## 📝 Exemples d'Utilisation

### Modale Simple
```html
<div class="modal">
    <div class="modal-content-dotted">
        <h2>Titre de la modale</h2>
        <form>
            <div class="form-group">
                <label>Champ</label>
                <input type="text">
            </div>
            <div class="form-actions">
                <button class="btn-secondary">Annuler</button>
                <button class="btn-primary">Enregistrer</button>
            </div>
        </form>
    </div>
</div>
```

### Section de Contenu
```html
<div class="dotted-section section-blue">
    <h3>Titre de la section</h3>
    <p>Contenu...</p>
</div>
```

## 🎨 Règles Importantes

1. **Cohérence** : Tous les formulaires doivent avoir le même style
2. **Bordures** : Toujours 3px dotted, jamais solid sauf pour les inputs
3. **Boutons** : Toujours avec contour (border), jamais juste un fond uni
4. **Espacement** : padding de 1.5rem à 2rem pour les sections
5. **Animations** : Transitions de 0.2s à 0.3s pour fluidité
