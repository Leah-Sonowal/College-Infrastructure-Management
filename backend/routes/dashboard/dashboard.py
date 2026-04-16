from flask import Blueprint, jsonify
from db import mysql

dashboard_bp = Blueprint('dashboard', __name__)

#Total no. of issues
@dashboard_bp.route('/dashboard/total-issues', methods=['GET'])
def total_issues():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Issue")
    count = cursor.fetchone()[0]
    cursor.close()

    return jsonify({"total_issues": count})

#Status count
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

#Issues by category
@issue_bp.route('/dashboard/category-count', methods=['GET'])
def category_count():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT issue_category, COUNT(*) 
        FROM Issue 
        GROUP BY issue_category
    """)

    data = cursor.fetchall()
    cursor.close()

    result = {}
    for row in data:
        result[row[0]] = row[1]

    return jsonify(result)

#User-specific view
@issue_bp.route('/dashboard/user/<int:user_id>', methods=['GET'])
def user_issues(user_id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT Issue.issue_id, Issue.description, Issue.status
        FROM Issue
        JOIN Reports ON Issue.issue_id = Reports.issue_id
        WHERE Reports.user_id = %s
    """, (user_id,))

    rows = cursor.fetchall()
    cursor.close()

    result = []
    for row in rows:
        result.append({
            "issue_id": row[0],
            "description": row[1],
            "status": row[2]
        })

    return jsonify(result)
