import logging
import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from db import mysql
from utils.validators import validate_registration

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


# ─────────────────────────────────────────────
# POST /register
# ─────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user. Hashes password before storage."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    errors = validate_registration(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    try:
        cursor = mysql.connection.cursor()

        # Check for duplicate email
        cursor.execute("SELECT user_id FROM User WHERE email = %s", (data['email'],))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Email already registered"}), 409

        # Hash password
        hashed_pw = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        cursor.execute("""
            INSERT INTO User (first_name, last_name, email, date_of_birth, user_type, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'],
            data['last_name'],
            data['email'],
            data['date_of_birth'],
            data['user_type'],
            hashed_pw
        ))
        mysql.connection.commit()
        new_id = cursor.lastrowid
        cursor.close()

        logger.info(f"New user registered: {data['email']} (id={new_id})")
        return jsonify({"message": "User registered successfully", "user_id": new_id}), 201

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# POST /login
# ─────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT access token."""
    data = request.get_json(silent=True)
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT user_id, password, user_type, first_name FROM User WHERE email = %s",
            (data['email'],)
        )
        user = cursor.fetchone()
        cursor.close()

        if not user:
            logger.warning(f"Login attempt for unknown email: {data['email']}")
            return jsonify({"error": "Invalid email or password"}), 401

        user_id, stored_hash, role, first_name = user

        if not bcrypt.checkpw(data['password'].encode('utf-8'), stored_hash.encode('utf-8')):
            logger.warning(f"Failed login attempt for: {data['email']}")
            return jsonify({"error": "Invalid email or password"}), 401

        # Embed role inside JWT claims
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={"role": role, "name": first_name}
        )

        logger.info(f"Successful login: {data['email']} (role={role})")
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user_id": user_id,
            "role": role,
            "name": first_name
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500
