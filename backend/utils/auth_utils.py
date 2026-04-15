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
