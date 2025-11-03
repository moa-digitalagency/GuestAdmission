#!/bin/bash

echo "🚀 Démarrage de l'application..."
echo ""

python3 init_database.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🌐 Lancement du serveur web..."
    exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
else
    echo ""
    echo "❌ Échec de l'initialisation de la base de données"
    exit 1
fi
