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
from .models.user import User

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'frontend', 'templates'),
            static_folder=os.path.join(base_dir, 'frontend', 'static'))
app.secret_key = os.environ.get("SESSION_SECRET")
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'frontend', 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
CORS(app)

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

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
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
