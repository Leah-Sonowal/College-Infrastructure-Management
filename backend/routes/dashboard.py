import logging
from flask import Blueprint, jsonify
from db import mysql
from utils.auth_utils import role_required

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)


# ─────────────────────────────────────────────
# GET /dashboard/summary
# ─────────────────────────────────────────────
@dashboard_bp.route('/dashboard/summary', methods=['GET'])
@role_required(['Admin', 'Faculty', 'Staff'])
def summary():
    """High-level counts for the admin dashboard."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(status = 'Pending') AS pending,
                SUM(status = 'In Progress') AS in_progress,
                SUM(status = 'Resolved') AS resolved,
                SUM(status = 'Escalated') AS escalated,
                SUM(status = 'Closed') AS closed
            FROM Issue
        """)
        row = cursor.fetchone()
        cursor.close()

        return jsonify({
            "total_issues": row[0],
            "pending": int(row[1] or 0),
            "in_progress": int(row[2] or 0),
            "resolved": int(row[3] or 0),
            "escalated": int(row[4] or 0),
            "closed": int(row[5] or 0)
        }), 200

    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# GET /dashboard/status-count
# ─────────────────────────────────────────────
@dashboard_bp.route('/dashboard/status-count', methods=['GET'])
@role_required(['Admin', 'Faculty', 'Staff'])
def status_count():
    """Count of issues grouped by status."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM Issue GROUP BY status")
        rows = cursor.fetchall()
        cursor.close()
        return jsonify({row[0]: row[1] for row in rows}), 200

    except Exception as e:
        logger.error(f"Status count error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# GET /dashboard/category-count
# ─────────────────────────────────────────────
@dashboard_bp.route('/dashboard/category-count', methods=['GET'])
@role_required(['Admin', 'Faculty', 'Staff'])
def category_count():
    """Count of issues grouped by category."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT issue_category, COUNT(*) FROM Issue GROUP BY issue_category")
        rows = cursor.fetchall()
        cursor.close()
        return jsonify({row[0]: row[1] for row in rows}), 200

    except Exception as e:
        logger.error(f"Category count error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# GET /dashboard/monthly-trend
# ─────────────────────────────────────────────
@dashboard_bp.route('/dashboard/monthly-trend', methods=['GET'])
@role_required(['Admin', 'Faculty', 'Staff'])
def monthly_trend():
    """Count of issues reported per month (last 12 months)."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT
                DATE_FORMAT(reported_date, '%Y-%m') AS month,
                COUNT(*) AS count
            FROM Issue
            WHERE reported_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month ASC
        """)
        rows = cursor.fetchall()
        cursor.close()

        return jsonify([{"month": r[0], "count": r[1]} for r in rows]), 200

    except Exception as e:
        logger.error(f"Monthly trend error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ─────────────────────────────────────────────
# GET /dashboard/technician-load
# ─────────────────────────────────────────────
@dashboard_bp.route('/dashboard/technician-load', methods=['GET'])
@role_required(['Admin', 'Faculty', 'Staff'])
def technician_load():
    """Number of active (non-resolved) issues per technician."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT
                t.technician_id,
                t.technician_name,
                t.specialization,
                t.technician_availability_status,
                COUNT(si.issue_id) AS active_issues
            FROM Technician t
            LEFT JOIN Has h ON t.technician_id = h.technician_id
            LEFT JOIN Scheduled_In si ON h.slot_id = si.slot_id
            LEFT JOIN Issue i ON si.issue_id = i.issue_id
                AND i.status NOT IN ('Resolved', 'Closed')
            GROUP BY t.technician_id, t.technician_name,
                     t.specialization, t.technician_availability_status
            ORDER BY active_issues DESC
        """)
        rows = cursor.fetchall()
        cursor.close()

        return jsonify([
            {
                "technician_id": r[0],
                "name": r[1],
                "specialization": r[2],
                "availability": r[3],
                "active_issues": r[4]
            }
            for r in rows
        ]), 200

    except Exception as e:
        logger.error(f"Technician load error: {e}")
        return jsonify({"error": "Internal server error"}), 500
