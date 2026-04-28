import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import config
from db import mysql
from routes.auth import auth_bp
from routes.issues import issue_bp
from routes.dashboard import dashboard_bp

# ─── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ─── App factory ──────────────────────────────────────────────────────────────
def create_app():
    app = Flask(__name__)

    # Security keys
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY

    # MySQL config
    app.config['MYSQL_HOST'] = config.MYSQL_HOST
    app.config['MYSQL_USER'] = config.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = config.MYSQL_DB
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # optional: dict rows

    # Extensions
    CORS(app)
    mysql.init_app(app)
    JWTManager(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(issue_bp)
    app.register_blueprint(dashboard_bp)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route('/', methods=['GET'])
    def health():
        return jsonify({"status": "ok", "message": "Infra Flow API is running"}), 200

    # ── Global error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Unhandled 500: {e}")
        return jsonify({"error": "Internal server error"}), 500

    logger.info("Infra Flow app initialised successfully")
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
