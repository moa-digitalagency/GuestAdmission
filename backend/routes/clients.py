from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required
from ..models.client import Client
from ..models.personne import Personne
from ..utils import serialize_rows, serialize_row

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/api/clients', methods=['GET'])
def get_clients():
    clients = Client.get_all()
    return jsonify(serialize_rows(clients))

@clients_bp.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = Client.get_by_id(client_id)
    if client:
        return jsonify(serialize_row(client))
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


@clients_bp.route('/api/clients/export-pdf', methods=['GET'])
@login_required
def export_clients_pdf():
    """Exporter la liste des clients en PDF"""
    from ..services.clients_export_service import ClientsExportService
    
    search = request.args.get('search', '')
    pays = request.args.get('pays', '')
    type_piece = request.args.get('type_piece', '')
    
    try:
        pdf_buffer = ClientsExportService.generate_clients_pdf(
            search_filter=search,
            pays_filter=pays,
            type_piece_filter=type_piece
        )
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'clients_export.pdf'
        )
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération du PDF: {str(e)}'}), 500
