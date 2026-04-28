import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import mysql
from utils.auth_utils import role_required
from utils.validators import validate_issue, validate_status_update

logger = logging.getLogger(__name__)
issue_bp = Blueprint('issues', __name__)


# ─────────────────────────────────────────────
# POST /issues  — Report a new issue
# ─────────────────────────────────────────────
@issue_bp.route('/issues', methods=['POST'])
@jwt_required()
def create_issue():
    """Any authenticated user can report an issue."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    errors = validate_issue(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    user_id = int(get_jwt_identity())

    try:
        cursor = mysql.connection.cursor()

        # Validate location if provided
        building = data.get('building_name')
        room = data.get('room_no')
        if building and room:
            cursor.execute(
                "SELECT 1 FROM Location WHERE building_name=%s AND room_no=%s",
                (building, room)
            )
            if not cursor.fetchone():
                cursor.close()
                return jsonify({"error": "Location not found"}), 404

        cursor.execute("""
            INSERT INTO Issue
              (issue_category, description, reported_date, status, proof_image, building_name, room_no)
            VALUES (%s, %s, %s, 'Pending', %s, %s, %s)
        """, (
            data['issue_category'],
            data['description'],
            datetime.now(),
            data.get('proof_image'),
            building,
            room
        ))
        issue_id = cursor.lastrowid

        # Create entry in Reports relationship table
        cursor.execute("""
            INSERT INTO Reports (user_id, issue_id, issue_category, report_time, urgency_flag)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            issue_id,
            data['issue_category'],
            datetime.now(),
            bool(data.get('urgency_flag', False))
        ))

        mysql.connection.commit()
        cursor.close()

        logger.info(f"Issue #{issue_id} created by user #{user_id}")
        return jsonify({"message": "Issue reported successfully", "issue_id": issue_id}), 201

    except Exception as e:
        logger.error(f"Create issue error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# GET /issues  — List all issues (admin/staff)
# ─────────────────────────────────────────────
@issue_bp.route('/issues', methods=['GET'])
@role_required(['Admin', 'Faculty', 'Staff'])
def get_all_issues():
    """Return all issues with optional status filter."""
    status_filter = request.args.get('status')

    try:
        cursor = mysql.connection.cursor()

        if status_filter:
            cursor.execute("""
                SELECT issue_id, issue_category, description,
                       reported_date, status, building_name, room_no
                FROM Issue
                WHERE status = %s
                ORDER BY reported_date DESC
            """, (status_filter,))
        else:
            cursor.execute("""
                SELECT issue_id, issue_category, description,
                       reported_date, status, building_name, room_no
                FROM Issue
                ORDER BY reported_date DESC
            """)

        rows = cursor.fetchall()
        cursor.close()

        issues = [
            {
                "issue_id": r[0],
                "issue_category": r[1],
                "description": r[2],
                "reported_date": str(r[3]),
                "status": r[4],
                "building_name": r[5],
                "room_no": r[6]
            }
            for r in rows
        ]
        return jsonify({"issues": issues, "count": len(issues)}), 200

    except Exception as e:
        logger.error(f"Get issues error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# GET /issues/<id>  — Get single issue
# ─────────────────────────────────────────────
@issue_bp.route('/issues/<int:issue_id>', methods=['GET'])
@jwt_required()
def get_issue(issue_id):
    """Fetch details for a specific issue."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT issue_id, issue_category, description,
                   reported_date, completion_date, status,
                   proof_image, building_name, room_no
            FROM Issue
            WHERE issue_id = %s
        """, (issue_id,))
        row = cursor.fetchone()
        cursor.close()

        if not row:
            return jsonify({"error": "Issue not found"}), 404

        return jsonify({
            "issue_id": row[0],
            "issue_category": row[1],
            "description": row[2],
            "reported_date": str(row[3]),
            "completion_date": str(row[4]) if row[4] else None,
            "status": row[5],
            "proof_image": row[6],
            "building_name": row[7],
            "room_no": row[8]
        }), 200

    except Exception as e:
        logger.error(f"Get issue #{issue_id} error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# PUT /issues/<id>  — Update issue status
# ─────────────────────────────────────────────
@issue_bp.route('/issues/<int:issue_id>', methods=['PUT'])
@role_required(['Admin', 'Faculty', 'Staff', 'Technician'])
def update_issue(issue_id):
    """Update status (and optionally completion_date) of an issue."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    errors = validate_status_update(data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT issue_id FROM Issue WHERE issue_id = %s", (issue_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Issue not found"}), 404

        completion_date = None
        if data['status'] in ('Resolved', 'Closed'):
            completion_date = datetime.now()

        cursor.execute("""
            UPDATE Issue
            SET status = %s, completion_date = %s
            WHERE issue_id = %s
        """, (data['status'], completion_date, issue_id))
        mysql.connection.commit()
        cursor.close()

        logger.info(f"Issue #{issue_id} status updated to '{data['status']}'")
        return jsonify({"message": "Issue updated successfully"}), 200

    except Exception as e:
        logger.error(f"Update issue #{issue_id} error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# DELETE /issues/<id>
# ─────────────────────────────────────────────
@issue_bp.route('/issues/<int:issue_id>', methods=['DELETE'])
@role_required(['Admin', 'Faculty'])
def delete_issue(issue_id):
    """Permanently delete an issue (admin/faculty only)."""
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT issue_id FROM Issue WHERE issue_id = %s", (issue_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Issue not found"}), 404

        cursor.execute("DELETE FROM Issue WHERE issue_id = %s", (issue_id,))
        mysql.connection.commit()
        cursor.close()

        logger.info(f"Issue #{issue_id} deleted")
        return jsonify({"message": "Issue deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Delete issue #{issue_id} error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# GET /users/<user_id>/issues  — User's own issues
# ─────────────────────────────────────────────
@issue_bp.route('/users/<int:user_id>/issues', methods=['GET'])
@jwt_required()
def get_user_issues(user_id):
    """Return issues reported by a specific user."""
    # Users can only see their own; admins/staff can see anyone's
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    caller_id = int(get_jwt_identity())

    if caller_id != user_id and claims.get('role') not in ('Admin', 'Faculty', 'Staff'):
        return jsonify({"error": "Forbidden"}), 403

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT i.issue_id, i.issue_category, i.description,
                   i.reported_date, i.status
            FROM Issue i
            JOIN Reports r ON i.issue_id = r.issue_id
            WHERE r.user_id = %s
            ORDER BY i.reported_date DESC
        """, (user_id,))
        rows = cursor.fetchall()
        cursor.close()

        issues = [
            {
                "issue_id": r[0],
                "issue_category": r[1],
                "description": r[2],
                "reported_date": str(r[3]),
                "status": r[4]
            }
            for r in rows
        ]
        return jsonify({"issues": issues, "count": len(issues)}), 200

    except Exception as e:
        logger.error(f"Get user #{user_id} issues error: {e}")
        return jsonify({"error": "Internal server error"}), 500
