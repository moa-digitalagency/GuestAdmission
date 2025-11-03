#!/usr/bin/env python3
"""Script pour tester tous les endpoints API de la page paramètres"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
    print("🔍 Test des endpoints API\n" + "="*60)
    
    # Créer une session pour conserver les cookies
    session = requests.Session()
    
    # 1. Test de connexion
    print("\n1️⃣ Test de connexion...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        if response.status_code in [200, 302]:
            print("   ✅ Connexion réussie")
        else:
            print(f"   ❌ Connexion échouée: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        return
    
    # 2. Test /api/current-user
    print("\n2️⃣ Test /api/current-user...")
    try:
        response = session.get(f"{BASE_URL}/api/current-user")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Données utilisateur: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Erreur: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 3. Test /api/etablissements
    print("\n3️⃣ Test /api/etablissements...")
    try:
        response = session.get(f"{BASE_URL}/api/etablissements?actif_only=false")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Nombre d'établissements: {len(data)}")
            if data:
                print(f"   Premier établissement: {data[0].get('nom', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 4. Test /api/chambres
    print("\n4️⃣ Test /api/chambres...")
    try:
        response = session.get(f"{BASE_URL}/api/chambres")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Nombre de chambres: {len(data)}")
            if data:
                print(f"   Première chambre: {data[0].get('nom', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 5. Test /api/personnels
    print("\n5️⃣ Test /api/personnels...")
    try:
        response = session.get(f"{BASE_URL}/api/personnels")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Nombre de personnels: {len(data)}")
            if data:
                print(f"   Premier personnel: {data[0].get('nom', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 6. Test page /parametres
    print("\n6️⃣ Test page /parametres...")
    try:
        response = session.get(f"{BASE_URL}/parametres", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Page accessible")
            print(f"   Taille de la réponse: {len(response.text)} caractères")
        elif response.status_code == 302:
            print(f"   ❌ Redirection vers: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "="*60)
    print("✅ Tests terminés\n")

if __name__ == "__main__":
    test_endpoints()
