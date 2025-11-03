import os
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required
from .routes.clients import clients_bp
from .routes.auth import auth_bp
from .routes.reservations import reservations_bp
from .routes.parametres import parametres_bp
from .routes.countries import countries_bp
from .models.user import User

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'frontend', 'templates'),
            static_folder=os.path.join(base_dir, 'frontend', 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login_page'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(reservations_bp)
app.register_blueprint(parametres_bp)
app.register_blueprint(countries_bp)

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/nouvelle-reservation')
@login_required
def nouvelle_reservation():
    return render_template('nouvelle_reservation.html')

@app.route('/reservations')
@login_required
def reservations_page():
    return render_template('reservations.html')

@app.route('/clients')
@login_required
def clients_page():
    return render_template('clients_list.html')

@app.route('/parametres')
@login_required
def parametres():
    return render_template('parametres.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
