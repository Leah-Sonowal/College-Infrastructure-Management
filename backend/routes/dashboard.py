from flask import Blueprint, jsonify, request
from db import mysql

dashboard_bp = Blueprint('dashboard', __name__)

# ================= TOTAL ISSUES =================
@dashboard_bp.route('/dashboard/total-issues', methods=['GET'])
def total_issues():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Issue")
    count = cursor.fetchone()[0]
    cursor.close()
    return jsonify({"total_issues": count})


# ================= STATUS COUNT =================
@dashboard_bp.route('/dashboard/status-count', methods=['GET'])
def status_count():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM Issue GROUP BY status")
    data = cursor.fetchall()
    cursor.close()

    result = {}
    for row in data:
        result[row[0]] = row[1]
    return jsonify(result)


# ================= CATEGORY COUNT =================
@dashboard_bp.route('/dashboard/category-count', methods=['GET'])
def category_count():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT issue_category, COUNT(*) FROM Issue GROUP BY issue_category")
    data = cursor.fetchall()
    cursor.close()

    result = {}
    for row in data:
        result[row[0]] = row[1]
    return jsonify(result)


# ================= USER-SPECIFIC ISSUES =================
@dashboard_bp.route('/dashboard/user/<int:user_id>', methods=['GET'])
def user_issues(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT Issue.issue_id, Issue.description, Issue.status, Issue.issue_category
        FROM Issue
        JOIN Reports ON Issue.issue_id = Reports.issue_id
        WHERE Reports.user_id = %s
        ORDER BY Issue.issue_id DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()

    return jsonify([{
        "issue_id": r[0],
        "description": r[1],
        "status": r[2],
        "category": r[3]
    } for r in rows])
