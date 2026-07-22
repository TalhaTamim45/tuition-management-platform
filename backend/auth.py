import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

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
