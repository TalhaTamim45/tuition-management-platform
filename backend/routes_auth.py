from flask import Blueprint, request, jsonify, g
from models import db, User
from auth import generate_token, generate_password_hash, check_password_hash, token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    phone = data.get('phone', '').strip()
    raw_role = str(data.get('role', 'client')).strip().lower()

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "error": "Name, email, and password are required."
        }), 400

    # Public registration choices MUST be strictly 'client' or 'tutor'
    if raw_role not in ['client', 'tutor']:
        return jsonify({
            "success": False,
            "error": "Invalid account role"
        }), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({
            "success": False,
            "error": "User with this email already exists."
        }), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=hashed_pw,
        role=raw_role,
        is_blocked=False
    )
    db.session.add(new_user)
    db.session.commit()

    token = generate_token(new_user.id)
    return jsonify({
        "success": True,
        "message": "User registered successfully.",
        "token": token,
        "user": new_user.to_dict()
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({
            "success": False,
            "error": "Email and password are required."
        }), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({
            "success": False,
            "error": "Invalid email or password."
        }), 401

    if getattr(user, 'is_blocked', False):
        return jsonify({
            "success": False,
            "error": "Account is blocked. Please contact support."
        }), 403

    token = generate_token(user.id)
    return jsonify({
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": user.to_dict()
    }), 200


@auth_bp.route('/api/auth/me', methods=['GET', 'OPTIONS'])
@token_required
def get_current_user():
    return jsonify({
        "success": True,
        "user": g.current_user.to_dict()
    }), 200
