from flask import Flask
from flask_cors import CORS
from db import mysql
import config

from routes.auth import auth_bp
from routes.issues import issue_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
CORS(app)

# DB Config
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(issue_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return {"message": "Infra Flow backend running ✅"}

if __name__ == '__main__':
    app.run(debug=True)
