from flask import Blueprint, jsonify, request
import json
import os

cities_bp = Blueprint('cities', __name__)

def get_data_file_path(filename):
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(backend_dir, 'data', filename)

@cities_bp.route('/api/pays', methods=['GET'])
def get_pays():
    try:
        with open(get_data_file_path('pays.json'), 'r', encoding='utf-8') as f:
            pays = json.load(f)
        return jsonify(pays)
    except Exception as e:
        print(f"Erreur lors de la lecture des pays: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des pays'}), 500

@cities_bp.route('/api/villes/<pays_code>', methods=['GET'])
def get_villes(pays_code):
    try:
        with open(get_data_file_path('villes.json'), 'r', encoding='utf-8') as f:
            villes_data = json.load(f)
        
        villes = villes_data.get(pays_code, [])
        return jsonify(villes)
    except Exception as e:
        print(f"Erreur lors de la lecture des villes: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des villes'}), 500

@cities_bp.route('/api/cities/<country_code>', methods=['GET'])
def get_cities(country_code):
    try:
        with open(get_data_file_path('villes.json'), 'r', encoding='utf-8') as f:
            villes_data = json.load(f)
        
        cities = villes_data.get(country_code.upper(), [])
        return jsonify({
            'country_code': country_code.upper(),
            'cities': cities
        })
    except Exception as e:
        print(f"Erreur lors de la lecture des villes: {e}")
        return jsonify({'error': 'Erreur lors de la récupération des villes'}), 500

@cities_bp.route('/api/cities/search', methods=['GET'])
def search_cities():
    query = request.args.get('q', '').lower()
    
    try:
        with open(get_data_file_path('villes.json'), 'r', encoding='utf-8') as f:
            villes_data = json.load(f)
        
        all_cities = []
        for country_code, cities in villes_data.items():
            for city in cities:
                if query in city.lower():
                    all_cities.append({
                        'name': city,
                        'country_code': country_code
                    })
        
        return jsonify(all_cities[:50])
    except Exception as e:
        print(f"Erreur lors de la recherche des villes: {e}")
        return jsonify({'error': 'Erreur lors de la recherche'}), 500
