from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(allowed_roles: list[str]):
    """
    Decorator that protects a route to specific roles.
    Roles are embedded in the JWT claims at login.

    Usage:
        @role_required(['Admin', 'Faculty'])
        def some_route():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get('role', '')

            if role not in allowed_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": f"Access requires one of: {', '.join(allowed_roles)}"
                }), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
