from flask import Blueprint, request, jsonify
from db import mysql
import bcrypt

auth_bp = Blueprint('auth', __name__)

# ================= REGISTER =================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    required = ['first_name', 'last_name', 'email', 'password', 'date_of_birth', 'user_type']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    password = data['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

    cursor = mysql.connection.cursor()

    # Check if email already exists
    cursor.execute("SELECT user_id FROM User WHERE email=%s", (data['email'],))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Email already registered"}), 409

    cursor.execute("""
        INSERT INTO User (first_name, last_name, email, date_of_birth, user_type, password)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['first_name'],
        data['last_name'],
        data['email'],
        data['date_of_birth'],
        data['user_type'],
        hashed_password
    ))

    mysql.connection.commit()
    user_id = cursor.lastrowid
    cursor.close()

    return jsonify({"message": "User registered successfully", "user_id": user_id})


# ================= LOGIN =================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT user_id, password, user_type, first_name FROM User WHERE email=%s", (data['email'],))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    stored_password = user[1]
    # Handle both bytes and string stored passwords
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')

    if bcrypt.checkpw(data['password'].encode('utf-8'), stored_password):
        return jsonify({
            "message": "Login successful",
            "user_id": user[0],
            "role": user[2],
            "name": user[3]
        })
    else:
        return jsonify({"error": "Invalid password"}), 401
