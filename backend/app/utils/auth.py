"""Authentication utilities."""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User


def jwt_required_custom(fn):
    """Custom JWT required decorator with user loading."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_active:
            return jsonify({"error": "User not found or inactive"}), 401
        
        return fn(*args, current_user=current_user, **kwargs)
    
    return wrapper
