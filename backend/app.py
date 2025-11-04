import os
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required
from .routes.clients import clients_bp
from .routes.auth import auth_bp
from .routes.sejours import sejours_bp
from .routes.parametres import parametres_bp
from .routes.countries import countries_bp
from .routes.chambres import chambres_bp
from .routes.etablissements import etablissements_bp
from .routes.data_management import data_bp
from .routes.personnels import personnels_bp
from .routes.extras import extras_bp
from .routes.statistics import statistics_bp
from .routes.mail import mail_bp
from .routes.calendars import calendars_bp
from .models.user import User
from .services.activity_logger import ActivityLoggerMiddleware

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'frontend', 'templates'),
            static_folder=os.path.join(base_dir, 'frontend', 'static'))
app.secret_key = os.environ.get("SESSION_SECRET")
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'frontend', 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
CORS(app)

ActivityLoggerMiddleware(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login_page'  # type: ignore

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(sejours_bp)
app.register_blueprint(parametres_bp)
app.register_blueprint(countries_bp)
app.register_blueprint(chambres_bp)
app.register_blueprint(etablissements_bp)
app.register_blueprint(data_bp)
app.register_blueprint(personnels_bp)
app.register_blueprint(extras_bp)
app.register_blueprint(statistics_bp)
app.register_blueprint(mail_bp)
app.register_blueprint(calendars_bp)

from .routes.activity_logs import activity_logs_bp
app.register_blueprint(activity_logs_bp)

from .routes.super_admin import super_admin_bp
app.register_blueprint(super_admin_bp)

from .routes.platform_admin import platform_admin_bp
app.register_blueprint(platform_admin_bp)

from .routes.tenant_admin import tenant_admin_bp
app.register_blueprint(tenant_admin_bp)

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Route de compatibilité - redirige selon le rôle"""
    if current_user.is_platform_admin():
        return redirect(url_for('platform_admin_dashboard'))
    elif current_user.is_admin():
        # Les tenant admins sont redirigés vers leur dashboard tenant
        return redirect(url_for('tenant_dashboard'))
    # Utilisateurs réguliers restent ici
    return render_template('dashboard.html')

@app.route('/nouveau-sejour')
@login_required
def nouveau_sejour():
    return render_template('nouveau_sejour.html')

@app.route('/sejours')
@login_required
def sejours_page():
    return render_template('sejours.html')

@app.route('/clients')
@login_required
def clients_page():
    return render_template('clients_list.html')

@app.route('/parametres')
@login_required
def parametres():
    return render_template('parametres.html')

@app.route('/statistiques')
@login_required
def statistiques():
    return render_template('statistiques.html')

@app.route('/extras')
@login_required
def extras_page():
    return render_template('extras.html')

@app.route('/pos-extras')
@login_required
def pos_extras():
    return render_template('pos_extras.html')

@app.route('/sejour/<int:sejour_id>')
@login_required
def sejour_detail(sejour_id):
    return render_template('sejour_detail.html', sejour_id=sejour_id)

@app.route('/messagerie')
@login_required
def messagerie():
    return render_template('messagerie.html')

@app.route('/calendriers')
@login_required
def calendriers():
    return render_template('calendriers.html')

@app.route('/super-admin')
@login_required
def super_admin_dashboard():
    """Route de compatibilité - redirige vers platform-admin"""
    if not current_user.is_super_admin():
        return redirect(url_for('tenant_dashboard'))
    return redirect(url_for('platform_admin_dashboard'))

@app.route('/platform-admin')
@login_required
def platform_admin_dashboard():
    """Dashboard pour les PLATFORM_ADMIN"""
    if not current_user.is_platform_admin():
        return redirect(url_for('tenant_dashboard'))
    return render_template('platform_admin_dashboard.html')

@app.route('/tenant')
@login_required
def tenant_dashboard():
    """Dashboard pour les tenant admins"""
    if current_user.is_platform_admin():
        return redirect(url_for('platform_admin_dashboard'))
    
    # Vérifier que l'utilisateur est bien un admin (tenant admin)
    if not current_user.is_admin():
        return redirect(url_for('dashboard'))
    
    return render_template('tenant_dashboard.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
