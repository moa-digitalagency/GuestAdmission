"""
Routes pour les statistiques
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from ..services.statistics_service import StatisticsService

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/api/statistics/global', methods=['GET'])
@login_required
def get_global_statistics():
    """Récupérer les statistiques globales"""
    stats = StatisticsService.get_global_statistics()
    return jsonify(stats)


@statistics_bp.route('/api/statistics/occupancy', methods=['GET'])
@login_required
def get_occupancy_rate():
    """Récupérer le taux d'occupation"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    stats = StatisticsService.get_occupancy_rate(
        etablissement_id=etablissement_id,
        date_debut=date_debut,
        date_fin=date_fin
    )
    return jsonify(stats)


@statistics_bp.route('/api/statistics/countries', methods=['GET'])
@login_required
def get_top_countries():
    """Récupérer les pays les plus fréquents"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    countries = StatisticsService.get_top_countries(
        etablissement_id=etablissement_id,
        limit=limit
    )
    return jsonify(countries)


@statistics_bp.route('/api/statistics/sejours-by-occupants', methods=['GET'])
@login_required
def get_sejours_by_occupants():
    """Récupérer les séjours avec le plus d'occupants"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    sejours = StatisticsService.get_sejours_by_occupants(
        etablissement_id=etablissement_id,
        limit=limit
    )
    return jsonify(sejours)


@statistics_bp.route('/api/statistics/sejours-by-rooms', methods=['GET'])
@login_required
def get_sejours_by_rooms():
    """Récupérer les séjours avec le plus de chambres"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    sejours = StatisticsService.get_sejours_by_rooms(
        etablissement_id=etablissement_id,
        limit=limit
    )
    return jsonify(sejours)


@statistics_bp.route('/api/statistics/revenue', methods=['GET'])
@login_required
def get_revenue_statistics():
    """Récupérer les statistiques de revenus"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    stats = StatisticsService.get_revenue_statistics(
        etablissement_id=etablissement_id,
        date_debut=date_debut,
        date_fin=date_fin
    )
    return jsonify(stats)


@statistics_bp.route('/api/statistics/monthly-trends', methods=['GET'])
@login_required
def get_monthly_trends():
    """Récupérer les tendances mensuelles"""
    etablissement_id = request.args.get('etablissement_id', type=int)
    months = request.args.get('months', 12, type=int)
    
    trends = StatisticsService.get_monthly_trends(
        etablissement_id=etablissement_id,
        months=months
    )
    return jsonify(trends)
