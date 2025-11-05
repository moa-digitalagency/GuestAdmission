#!/usr/bin/env python3
"""
Script pour remplacer 'réservation' par 'séjour' dans tout le codebase
Note: Ce script NE modifie PAS les noms de tables/colonnes de la base de données
      pour éviter de casser les données existantes.
"""

import os
import re
from pathlib import Path

# Mappings de remplacement
REPLACEMENTS = {
    # Français
    'réservations': 'séjours',
    'Réservations': 'Séjours',
    'RÉSERVATIONS': 'SÉJOURS',
    'Réservation': 'Séjour',
    'réservation': 'séjour',
    'RÉSERVATION': 'SÉJOUR',
    # Anglais
    'reservations': 'sejours',
    'Reservations': 'Sejours',
    'RESERVATIONS': 'SEJOURS',
    'Reservation': 'Sejour',
    'reservation': 'sejour',
    'RESERVATION': 'SEJOUR',
}

# Fichiers et dossiers à ignorer
IGNORE_PATTERNS = [
    '.git/',
    '__pycache__/',
    'node_modules/',
    '.pythonlibs/',
    'venv/',
    'env/',
    '.replit',
    'uv.lock',
    'replace_reservation_sejour.py',  # Ce script lui-même
    'migrations/',  # Ne pas modifier les migrations déjà executées
    'init_database.py',  # Ne pas modifier l'init (tables SQL)
]

# Extensions de fichiers à traiter
FILE_EXTENSIONS = [
    '.py', '.js', '.html', '.css', '.md', '.txt', '.json',
    '.ts', '.jsx', '.tsx', '.vue'
]

# Patterns à NE PAS remplacer (noms de tables SQL, colonnes, etc.)
SKIP_PATTERNS = [
    r'CREATE TABLE.*reservations',  # Créations de table
    r'FROM reservations',  # Requêtes SQL FROM
    r'JOIN reservations',  # Requêtes SQL JOIN
    r'INSERT INTO reservations',  # Requêtes SQL INSERT
    r'UPDATE reservations',  # Requêtes SQL UPDATE
    r'DELETE FROM reservations',  # Requêtes SQL DELETE
    r'reservations\.', # Références de colonnes SQL
    r'numero_reservation',  # Nom de colonne
    r'reservation_id',  # Nom de colonne FK
]

def should_ignore(file_path):
    """Vérifier si le fichier doit être ignoré"""
    path_str = str(file_path)
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def should_skip_line(line):
    """Vérifier si une ligne contient des patterns SQL à ne pas modifier"""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False

def replace_in_file(file_path):
    """Remplacer dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # Remplacer ligne par ligne pour éviter de modifier les patterns SQL
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Ne pas modifier les lignes avec des patterns SQL
            if should_skip_line(line):
                new_lines.append(line)
                continue
            
            # Appliquer les remplacements
            modified_line = line
            for old, new in REPLACEMENTS.items():
                modified_line = modified_line.replace(old, new)
            
            if modified_line != line:
                modified = True
            
            new_lines.append(modified_line)
        
        if modified:
            new_content = '\n'.join(new_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        return False
    
    except Exception as e:
        print(f"  ❌ Erreur avec {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔄 Remplacement de 'réservation' par 'séjour' dans le codebase...\n")
    
    modified_files = []
    
    # Parcourir tous les fichiers
    for root, dirs, files in os.walk('.'):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if not any(pattern.rstrip('/') in d for pattern in IGNORE_PATTERNS)]
        
        for file in files:
            file_path = Path(root) / file
            
            # Vérifier l'extension
            if file_path.suffix not in FILE_EXTENSIONS:
                continue
            
            # Vérifier si doit être ignoré
            if should_ignore(file_path):
                continue
            
            # Remplacer
            if replace_in_file(file_path):
                modified_files.append(str(file_path))
                print(f"  ✅ {file_path}")
    
    print(f"\n✅ Terminé! {len(modified_files)} fichier(s) modifié(s)\n")
    
    if modified_files:
        print("Fichiers modifiés:")
        for f in modified_files:
            print(f"  - {f}")

if __name__ == '__main__':
    main()
