from flask import Blueprint, request, jsonify
from db import mysql
import bcrypt

auth_bp = Blueprint('auth', __name__)

# ================= REGISTER =================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    password = data['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    cursor = mysql.connection.cursor()

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
    cursor.close()

    return jsonify({"message": "User registered successfully"})


# ================= LOGIN ================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT user_id, password, user_type FROM User WHERE email=%s", (data['email'],))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.checkpw(data['password'].encode('utf-8'), user[1].encode('utf-8')):
        return jsonify({
            "message": "Login successful",
            "user_id": user[0],
            "role": user[2]   # 🔥 important
        })
    else:
        return jsonify({"error": "Invalid password"}), 401
