import os
from flask import Flask, render_template
from flask_cors import CORS
from .config.database import init_db
from .routes.clients import clients_bp

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'frontend', 'templates'),
            static_folder=os.path.join(base_dir, 'frontend', 'static'))
CORS(app)

app.register_blueprint(clients_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clients')
def clients_page():
    return render_template('clients.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
