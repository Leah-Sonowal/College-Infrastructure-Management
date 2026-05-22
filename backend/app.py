from flask import Flask, send_from_directory
from flask_cors import CORS
from db import mysql
import config
import os

from routes.auth import auth_bp
from routes.issues import issue_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__,
            static_folder='frontend',
            static_url_path='')
CORS(app)

app.config['MYSQL_HOST']     = config.MYSQL_HOST
app.config['MYSQL_USER']     = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB']       = config.MYSQL_DB

mysql.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(issue_bp)
app.register_blueprint(dashboard_bp)

# Serve any frontend file by name
@app.route('/<path:filename>')
def serve_frontend(filename):
    return send_from_directory('frontend', filename)


# Serve front.html at root
@app.route('/')
def home():
    return send_from_directory('frontend', 'front.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
