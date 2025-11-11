#!/bin/bash

set -euo pipefail

echo "🚀 Démarrage de l'application..."
echo ""

python3 init_database.py

echo ""
echo "🌐 Lancement du serveur web..."

WORKERS=${GUNICORN_WORKERS:-4}
RELOAD_FLAG=""

if [ "${FLASK_ENV:-production}" = "development" ]; then
    echo "Mode développement détecté - rechargement automatique activé"
    RELOAD_FLAG="--reload"
    WORKERS=1
fi

exec gunicorn --bind 0.0.0.0:5000 --reuse-port --workers $WORKERS $RELOAD_FLAG main:app
