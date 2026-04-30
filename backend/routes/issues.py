from flask import Blueprint, request, jsonify
from db import mysql

issue_bp = Blueprint('issue', __name__)

# ================= GET ALL ISSUES =================
@issue_bp.route('/issues', methods=['GET'])
def get_issues():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT i.issue_id, i.description, i.status, i.issue_category,
               i.reported_date, i.building_name, i.room_no
        FROM Issue i
        ORDER BY i.reported_date DESC
    """)
    rows = cursor.fetchall()
    cursor.close()

    result = []
    for r in rows:
        result.append({
            "issue_id": r[0],
            "description": r[1],
            "status": r[2],
            "category": r[3],
            "reported_date": str(r[4]) if r[4] else None,
            "building_name": r[5],
            "room_no": r[6]
        })
    return jsonify(result)


# ================= GET SINGLE ISSUE =================
@issue_bp.route('/issues/<int:id>', methods=['GET'])
def get_issue(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT issue_id, description, status, issue_category FROM Issue WHERE issue_id=%s", (id,))
    r = cursor.fetchone()
    cursor.close()

    if not r:
        return jsonify({"error": "Issue not found"}), 404

    return jsonify({"issue_id": r[0], "description": r[1], "status": r[2], "category": r[3]})


# ================= CREATE ISSUE =================
@issue_bp.route('/issues', methods=['POST'])
def create_issue():
    data = request.json

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO Issue (issue_category, description, reported_date, status)
        VALUES (%s, %s, NOW(), 'Pending')
    """, (data['category'], data['description']))
    mysql.connection.commit()
    issue_id = cursor.lastrowid

    # Link to Reports table if user_id provided
    user_id = data.get('user_id')
    if user_id:
        cursor.execute("""
            INSERT INTO Reports (user_id, issue_id, issue_category, report_time, urgency_flag)
            VALUES (%s, %s, %s, NOW(), %s)
        """, (user_id, issue_id, data['category'], data.get('urgency', False)))
        mysql.connection.commit()

    cursor.close()
    return jsonify({"message": "Issue reported successfully", "issue_id": issue_id})


# ================= UPDATE STATUS =================
@issue_bp.route('/issues/update-status/<int:id>', methods=['PUT'])
def update_status(id):
    data = request.json
    role = request.headers.get('role')

    if role not in ['Faculty', 'Staff', 'Admin']:
        return jsonify({"error": "Unauthorized access"}), 403

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE Issue SET status=%s WHERE issue_id=%s", (data['status'], id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Status updated successfully"})


# ================= ASSIGN TECHNICIAN =================
@issue_bp.route('/issues/assign', methods=['POST'])
def assign_technician():
    data = request.json
    # data: { issue_id, technician_id, slot_date, slot_start, slot_end }

    cursor = mysql.connection.cursor()

    # Create a slot
    cursor.execute("""
        INSERT INTO Slot (slot_date, slot_start_time, slot_end_time, slot_status)
        VALUES (%s, %s, %s, 'Booked')
    """, (data['slot_date'], data['slot_start'], data['slot_end']))
    mysql.connection.commit()
    slot_id = cursor.lastrowid

    # Link technician to slot (Has table)
    cursor.execute("""
        INSERT INTO Has (slot_id, technician_id, technician_availability_status)
        VALUES (%s, %s, 'Busy')
    """, (slot_id, data['technician_id']))

    # Schedule issue in slot
    cursor.execute("""
        INSERT INTO Scheduled_In (issue_id, slot_id, scheduled_date)
        VALUES (%s, %s, %s)
    """, (data['issue_id'], slot_id, data['slot_date']))

    # Update issue status
    cursor.execute("UPDATE Issue SET status='Scheduled' WHERE issue_id=%s", (data['issue_id'],))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Technician assigned successfully"})


# ================= GET ALL TECHNICIANS =================
@issue_bp.route('/technicians', methods=['GET'])
def get_technicians():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT technician_id, technician_name, specialization, technician_availability_status
        FROM Technician
    """)
    rows = cursor.fetchall()
    cursor.close()

    return jsonify([{
        "technician_id": r[0],
        "name": r[1],
        "specialization": r[2],
        "status": r[3]
    } for r in rows])
