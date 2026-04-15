from functools import wraps
from flask import request, jsonify

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            role = request.headers.get('role')
            # role will be sent from frontend

            if role not in allowed_roles:
                return jsonify({"error": "Unauthorized access"}), 403

            return func(*args, **kwargs)

        return wrapper
    return decorator

from utils.auth_utils import role_required

@issue_bp.route('/update-status/<int:id>', methods=['PUT'])
@role_required(['Faculty', 'Staff'])  # Admin roles
def update_status(id):
    data = request.json

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE Issue SET status=%s WHERE issue_id=%s", (data['status'], id))
    mysql.connection.commit()
    cursor.close()



    return jsonify({"message": "Status updated"})
