from flask import Blueprint, jsonify, request
from flask_login import login_required
import requests

cities_bp = Blueprint('cities', __name__)

CITIES_CACHE = {}

def get_cities_for_country(country_code):
    """
    Récupère les villes pour un pays donné.
    Note: Pour une implémentation complète, vous pouvez utiliser:
    - GeoDB Cities API (freemium)
    - Country State City API
    - Ou une base de données locale de villes
    
    Pour l'instant, nous retournons les capitales depuis REST Countries API.
    """
    if country_code in CITIES_CACHE:
        return CITIES_CACHE[country_code]
    
    try:
        response = requests.get(f'https://restcountries.com/v3.1/alpha/{country_code}', timeout=10)
        response.raise_for_status()
        country_data = response.json()[0]
        
        cities = []
        
        if country_data.get('capital'):
            for capital in country_data['capital']:
                cities.append({
                    'name': capital,
                    'type': 'capital',
                    'country_code': country_code,
                    'country_name': country_data.get('name', {}).get('common', '')
                })
        
        CITIES_CACHE[country_code] = cities
        return cities
    
    except Exception as e:
        print(f"Erreur récupération villes pour {country_code}: {e}")
        return []

@cities_bp.route('/api/cities/<country_code>', methods=['GET'])
@login_required
def get_cities(country_code):
    """
    Retourne les villes principales d'un pays.
    Note: Actuellement retourne seulement les capitales.
    Pour une liste complète, vous devrez intégrer une API de villes dédiée.
    """
    cities = get_cities_for_country(country_code.upper())
    
    return jsonify({
        'country_code': country_code.upper(),
        'cities': cities,
        'note': 'Liste limitée aux capitales. Pour une liste complète, intégrez GeoDB Cities API ou Country State City API.'
    })

@cities_bp.route('/api/cities/search', methods=['GET'])
@login_required
def search_cities():
    """
    Recherche de villes par nom.
    Note: Fonctionnalité limitée sans API de villes dédiée.
    """
    query = request.args.get('q', '').lower()
    
    all_cities = []
    for country_code, cities in CITIES_CACHE.items():
        for city in cities:
            if query in city['name'].lower():
                all_cities.append(city)
    
    return jsonify(all_cities[:50])
