from flask import Blueprint, jsonify
from flask_login import login_required
import requests
import json

countries_bp = Blueprint('countries', __name__)

COUNTRIES_CACHE = None

def get_all_countries():
    """Récupère tous les pays depuis REST Countries API avec mise en cache"""
    global COUNTRIES_CACHE
    
    if COUNTRIES_CACHE is not None:
        return COUNTRIES_CACHE
    
    try:
        response = requests.get('https://restcountries.com/v3.1/all', timeout=10)
        response.raise_for_status()
        countries_data = response.json()
        
        formatted_countries = []
        for country in countries_data:
            try:
                common_name = country.get('name', {}).get('common', '')
                official_name = country.get('name', {}).get('official', '')
                
                currencies = {}
                if 'currencies' in country and country['currencies']:
                    for code, details in country['currencies'].items():
                        currencies[code] = {
                            'name': details.get('name', ''),
                            'symbol': details.get('symbol', '')
                        }
                
                capital = country.get('capital', [''])[0] if country.get('capital') else ''
                
                flag_png = country.get('flags', {}).get('png', '')
                flag_svg = country.get('flags', {}).get('svg', '')
                flag_alt = country.get('flags', {}).get('alt', '')
                
                formatted_country = {
                    'name': common_name,
                    'official_name': official_name,
                    'code': country.get('cca2', ''),
                    'code3': country.get('cca3', ''),
                    'capital': capital,
                    'region': country.get('region', ''),
                    'subregion': country.get('subregion', ''),
                    'population': country.get('population', 0),
                    'currencies': currencies,
                    'languages': country.get('languages', {}),
                    'flag': {
                        'png': flag_png,
                        'svg': flag_svg,
                        'alt': flag_alt,
                        'emoji': country.get('flag', '')
                    },
                    'timezones': country.get('timezones', []),
                    'latlng': country.get('latlng', [])
                }
                
                formatted_countries.append(formatted_country)
            except Exception as e:
                print(f"Erreur formatage pays: {e}")
                continue
        
        formatted_countries.sort(key=lambda x: x['name'])
        COUNTRIES_CACHE = formatted_countries
        
        return formatted_countries
    
    except Exception as e:
        print(f"Erreur récupération pays: {e}")
        return []

@countries_bp.route('/api/countries', methods=['GET'])
@login_required
def list_countries():
    """Retourne la liste de tous les pays avec leurs informations"""
    countries = get_all_countries()
    return jsonify(countries)

@countries_bp.route('/api/countries/<country_code>', methods=['GET'])
@login_required
def get_country(country_code):
    """Retourne les détails d'un pays spécifique"""
    countries = get_all_countries()
    country = next((c for c in countries if c['code'] == country_code.upper() or c['code3'] == country_code.upper()), None)
    
    if not country:
        return jsonify({'error': 'Pays non trouvé'}), 404
    
    return jsonify(country)

@countries_bp.route('/api/countries/search/<query>', methods=['GET'])
@login_required
def search_countries(query):
    """Recherche des pays par nom"""
    countries = get_all_countries()
    query_lower = query.lower()
    
    results = [c for c in countries if query_lower in c['name'].lower() or query_lower in c['official_name'].lower()]
    
    return jsonify(results)

@countries_bp.route('/api/currencies', methods=['GET'])
@login_required
def list_currencies():
    """Retourne la liste unique de toutes les devises"""
    countries = get_all_countries()
    currencies = {}
    
    for country in countries:
        for code, details in country.get('currencies', {}).items():
            if code not in currencies:
                currencies[code] = {
                    'code': code,
                    'name': details['name'],
                    'symbol': details.get('symbol', ''),
                    'countries': []
                }
            currencies[code]['countries'].append(country['name'])
    
    currency_list = list(currencies.values())
    currency_list.sort(key=lambda x: x['code'])
    
    return jsonify(currency_list)
