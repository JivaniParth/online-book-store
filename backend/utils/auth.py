import re
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return "Password must be at least 6 characters long"
    
    # Add more validation rules if needed
    # if not re.search(r"[A-Z]", password):
    #     return "Password must contain at least one uppercase letter"
    # if not re.search(r"[a-z]", password):
    #     return "Password must contain at least one lowercase letter"
    # if not re.search(r"\d", password):
    #     return "Password must contain at least one digit"
    
    return None

def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None

def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function