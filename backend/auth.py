import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

SECRET_KEY = "tuition_platform_secret_key_cse309_assessment4"

def generate_token(user_id):
    """Generate JWT token valid for 24 hours."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_required(f):
    """Decorator to enforce authentication on protected endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({"success": True}), 200

        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({
                "success": False,
                "error": "Authentication token missing. Please log in."
            }), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                return jsonify({
                    "success": False,
                    "error": "Invalid token user not found."
                }), 401
            
            # Check if user account is blocked
            if getattr(current_user, 'is_blocked', False):
                return jsonify({
                    "success": False,
                    "error": "Your account has been blocked. Please contact support."
                }), 403

            g.current_user = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": "Token has expired. Please log in again."
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "error": "Invalid token provided."
            }), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to enforce admin role authorization."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({"success": True}), 200

        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        if g.current_user.role.lower() != 'admin':
            return jsonify({
                "success": False,
                "error": "Admin privilege required. Access denied."
            }), 403

        return f(*args, **kwargs)
    return decorated
