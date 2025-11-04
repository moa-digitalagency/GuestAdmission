#!/usr/bin/env python3
"""
Script de test des fonctionnalités principales de l'application
"""
import sys
import os

os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL'))

from backend.models.user import User
from backend.models.etablissement import Etablissement
from backend.models.client import Client
from backend.models.reservation import Reservation
from backend.models.activity_log import ActivityLog

def test_database_connection():
    """Test de connexion à la base de données"""
    print("🔍 Test: Connexion à la base de données...")
    try:
        users = User.get_all()
        print(f"✅ Connexion réussie - {len(users)} utilisateur(s) trouvé(s)")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_users():
    """Test du système utilisateurs"""
    print("\n🔍 Test: Système utilisateurs...")
    try:
        users = User.get_all()
        if users:
            user = users[0]
            print(f"✅ {len(users)} utilisateur(s) - Exemple: {user.get('username', 'N/A')}")
            return True
        else:
            print("⚠️  Aucun utilisateur trouvé")
            return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_etablissements():
    """Test du système établissements"""
    print("\n🔍 Test: Système établissements...")
    try:
        etablissements = Etablissement.get_all()
        if etablissements:
            etab = etablissements[0]
            print(f"✅ {len(etablissements)} établissement(s) - Exemple: {etab.get('nom_etablissement', 'N/A')}")
            return True
        else:
            print("⚠️  Aucun établissement trouvé")
            return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_reservations():
    """Test du système réservations/séjours"""
    print("\n🔍 Test: Système réservations/séjours...")
    try:
        reservations = Reservation.get_all(limit=10)
        print(f"✅ {len(reservations)} réservation(s) trouvée(s)")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_clients():
    """Test du système clients"""
    print("\n🔍 Test: Système clients...")
    try:
        clients = Client.get_all(limit=10)
        print(f"✅ {len(clients)} client(s) trouvé(s)")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_activity_logs():
    """Test du système de logs d'activité"""
    print("\n🔍 Test: Système logs d'activité...")
    try:
        logs = ActivityLog.get_all(limit=10)
        count = ActivityLog.get_count()
        print(f"✅ {count} log(s) d'activité trouvé(s)")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Exécuter tous les tests"""
    print("=" * 60)
    print("🧪 TEST DES FONCTIONNALITÉS DE L'APPLICATION")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_users,
        test_etablissements,
        test_reservations,
        test_clients,
        test_activity_logs
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSULTATS: {sum(results)}/{len(results)} tests réussis")
    print("=" * 60)
    
    if all(results):
        print("\n✅ Tous les tests sont passés avec succès!")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué")
        return 1

if __name__ == '__main__':
    sys.exit(main())
