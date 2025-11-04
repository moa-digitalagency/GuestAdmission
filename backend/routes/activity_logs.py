from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend.models.activity_log import ActivityLog
from datetime import datetime, timedelta

activity_logs_bp = Blueprint('activity_logs', __name__)


@activity_logs_bp.route('/activity-logs')
@login_required
def activity_logs_page():
    """
    Page d'affichage des logs d'activité
    """
    return render_template('activity_logs.html')


@activity_logs_bp.route('/api/activity-logs')
@login_required
def get_activity_logs():
    """
    API pour récupérer les logs d'activité avec pagination et filtres
    """
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(200, max(1, int(request.args.get('per_page', 50))))
        user_id = request.args.get('user_id', None)
        action = request.args.get('action', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        if user_id:
            user_id = int(user_id)
            if user_id < 0:
                raise ValueError("Invalid user_id")
        
        if action and len(action) > 100:
            raise ValueError("Action string too long")
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        offset = (page - 1) * per_page
        
        logs = ActivityLog.get_all(
            limit=per_page,
            offset=offset,
            user_id=user_id,
            action=action,
            start_date=start_date,
            end_date=end_date
        )
        
        total_count = ActivityLog.get_count(
            user_id=user_id,
            action=action,
            start_date=start_date,
            end_date=end_date
        )
        
        logs_list = []
        for log in logs:
            logs_list.append({
                'id': log['id'],
                'user_id': log['user_id'],
                'username': log['username'],
                'user_nom': log.get('user_nom', ''),
                'user_prenom': log.get('user_prenom', ''),
                'action': log['action'],
                'route': log['route'],
                'method': log['method'],
                'ip_address': log['ip_address'],
                'user_agent': log['user_agent'],
                'status_code': log['status_code'],
                'details': log['details'],
                'created_at': log['created_at'].isoformat() if log['created_at'] else None
            })
        
        return jsonify({
            'success': True,
            'logs': logs_list,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@activity_logs_bp.route('/api/activity-logs/<int:log_id>')
@login_required
def get_activity_log(log_id):
    """
    API pour récupérer un log spécifique
    """
    try:
        log = ActivityLog.get_by_id(log_id)
        
        if not log:
            return jsonify({
                'success': False,
                'error': 'Log non trouvé'
            }), 404
        
        return jsonify({
            'success': True,
            'log': {
                'id': log['id'],
                'user_id': log['user_id'],
                'username': log['username'],
                'user_nom': log.get('user_nom', ''),
                'user_prenom': log.get('user_prenom', ''),
                'action': log['action'],
                'route': log['route'],
                'method': log['method'],
                'ip_address': log['ip_address'],
                'user_agent': log['user_agent'],
                'status_code': log['status_code'],
                'details': log['details'],
                'created_at': log['created_at'].isoformat() if log['created_at'] else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@activity_logs_bp.route('/api/activity-logs/user-stats/<int:user_id>')
@login_required
def get_user_activity_stats(user_id):
    """
    API pour obtenir les statistiques d'activité d'un utilisateur
    """
    try:
        if user_id < 0:
            return jsonify({'success': False, 'error': 'Invalid user_id'}), 400
        
        days = min(365, max(1, int(request.args.get('days', 30))))
        stats = ActivityLog.get_user_statistics(user_id, days)
        
        stats_list = []
        for stat in stats:
            stats_list.append({
                'action': stat['action'],
                'count': stat['count'],
                'last_action': stat['last_action'].isoformat() if stat['last_action'] else None
            })
        
        return jsonify({
            'success': True,
            'stats': stats_list,
            'period_days': days
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@activity_logs_bp.route('/api/activity-logs/export')
@login_required
def export_activity_logs():
    """
    API pour exporter les logs d'activité en CSV
    """
    try:
        from flask import Response
        import csv
        from io import StringIO
        
        user_id = request.args.get('user_id', None)
        action = request.args.get('action', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        if user_id:
            user_id = int(user_id)
            if user_id < 0:
                raise ValueError("Invalid user_id")
        
        if action and len(action) > 100:
            raise ValueError("Action string too long")
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        logs = ActivityLog.get_all(
            limit=10000,
            offset=0,
            user_id=user_id,
            action=action,
            start_date=start_date,
            end_date=end_date
        )
        
        si = StringIO()
        writer = csv.writer(si)
        
        writer.writerow([
            'ID', 'Utilisateur', 'Nom', 'Prénom', 'Action', 
            'Route', 'Méthode', 'IP', 'Code Statut', 'Date/Heure'
        ])
        
        for log in logs:
            writer.writerow([
                log['id'],
                log['username'],
                log.get('user_nom', ''),
                log.get('user_prenom', ''),
                log['action'],
                log['route'],
                log['method'],
                log['ip_address'],
                log['status_code'],
                log['created_at'].strftime('%Y-%m-%d %H:%M:%S') if log['created_at'] else ''
            ])
        
        output = si.getvalue()
        
        return Response(
            output,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=activity_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
