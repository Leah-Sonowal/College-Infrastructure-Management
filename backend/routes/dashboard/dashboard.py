from flask import Blueprint, jsonify
from db import mysql

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/total-issues', methods=['GET'])
def total_issues():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Issue")
    count = cursor.fetchone()[0]
    cursor.close()

    return jsonify({"total_issues": count})

@dashboard_bp.route('/dashboard/status-count', methods=['GET'])
def status_count():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT status, COUNT(*) 
        FROM Issue 
        GROUP BY status
    """)

    data = cursor.fetchall()
    cursor.close()

    result = {}
    for row in data:
        result[row[0]] = row[1]

    return jsonify(result)

