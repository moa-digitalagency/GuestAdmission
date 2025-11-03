from flask import Flask, render_template
from flask_cors import CORS
from backend.config.database import init_db
from backend.routes.clients import clients_bp

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
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
