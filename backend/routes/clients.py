from flask import Blueprint, request, jsonify
from ..models.client import Client

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/api/clients', methods=['GET'])
def get_clients():
    clients = Client.get_all()
    return jsonify(clients)

@clients_bp.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = Client.get_by_id(client_id)
    if client:
        return jsonify(client)
    return jsonify({'error': 'Client non trouvé'}), 404

@clients_bp.route('/api/clients', methods=['POST'])
def create_client():
    data = request.get_json()
    client_id = Client.create(data)
    return jsonify({'id': client_id, 'message': 'Client créé avec succès'}), 201

@clients_bp.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    data = request.get_json()
    Client.update(client_id, data)
    return jsonify({'message': 'Client mis à jour avec succès'})

@clients_bp.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    Client.delete(client_id)
    return jsonify({'message': 'Client supprimé avec succès'})
