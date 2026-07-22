from flask import Blueprint, request, jsonify, g
from models import db, User, TuitionPost
from auth import token_required, admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/dashboard', methods=['GET', 'OPTIONS'])
@token_required
@admin_required
def get_admin_dashboard():
    """
    GET /api/admin/dashboard
    Returns summary statistics for the admin dashboard.
    """
    total_users = User.query.count()
    total_clients = User.query.filter_by(role='client').count()
    total_tutors = User.query.filter_by(role='tutor').count()
    total_posts = TuitionPost.query.count()
    open_posts = TuitionPost.query.filter_by(status='open').count()
    closed_posts = TuitionPost.query.filter_by(status='closed').count()

    return jsonify({
        "success": True,
        "total_users": total_users,
        "total_clients": total_clients,
        "total_tutors": total_tutors,
        "total_tuition_posts": total_posts,
        "open_tuition_posts": open_posts,
        "closed_tuition_posts": closed_posts,
        "total_applications": 0,
        "total_reported_items": 0
    }), 200


@admin_bp.route('/api/admin/users', methods=['GET', 'OPTIONS'])
@token_required
@admin_required
def get_admin_users():
    """
    GET /api/admin/users
    Fetch all users with optional search and filtering.
    """
    search_query = request.args.get('search', '').strip().lower()
    role_filter = request.args.get('role', '').strip().lower()
    status_filter = request.args.get('status', '').strip().lower()

    query = User.query

    if search_query:
        query = query.filter(
            (User.name.ilike(f"%{search_query}%")) |
            (User.email.ilike(f"%{search_query}%"))
        )

    if role_filter and role_filter in ['client', 'tutor', 'admin']:
        query = query.filter_by(role=role_filter)

    if status_filter == 'blocked':
        query = query.filter_by(is_blocked=True)
    elif status_filter == 'active':
        query = query.filter_by(is_blocked=False)

    users = query.order_by(User.created_at.desc()).all()
    return jsonify({
        "success": True,
        "count": len(users),
        "users": [user.to_dict() for user in users]
    }), 200


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['GET', 'OPTIONS'])
@token_required
@admin_required
def get_admin_user_details(user_id):
    """
    GET /api/admin/users/<user_id>
    Retrieve single user details by ID.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    user_data = user.to_dict()
    user_data['posts_count'] = TuitionPost.query.filter_by(user_id=user.id).count()
    return jsonify({
        "success": True,
        "user": user_data
    }), 200


@admin_bp.route('/api/admin/users/<int:user_id>/status', methods=['PATCH', 'OPTIONS'])
@token_required
@admin_required
def update_user_status(user_id):
    """
    PATCH /api/admin/users/<user_id>/status
    Block or unblock a user.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    # Prevent admin from blocking their own account
    if user.id == g.current_user.id:
        return jsonify({
            "success": False,
            "error": "Cannot block your own admin account."
        }), 400

    data = request.get_json() or {}
    if 'is_blocked' in data:
        user.is_blocked = bool(data['is_blocked'])
    else:
        # Toggle status if not explicitly provided
        user.is_blocked = not user.is_blocked

    db.session.commit()
    status_str = "blocked" if user.is_blocked else "unblocked"
    return jsonify({
        "success": True,
        "message": f"User {user.name} has been {status_str} successfully.",
        "user": user.to_dict()
    }), 200


@admin_bp.route('/api/admin/tuition-posts', methods=['GET', 'OPTIONS'])
@token_required
@admin_required
def get_admin_tuition_posts():
    """
    GET /api/admin/tuition-posts
    Retrieve all tuition posts across all users for admin management.
    """
    posts = TuitionPost.query.order_by(TuitionPost.created_at.desc()).all()
    return jsonify({
        "success": True,
        "count": len(posts),
        "posts": [post.to_dict() for post in posts]
    }), 200


@admin_bp.route('/api/admin/tuition-posts/<int:post_id>/status', methods=['PATCH', 'OPTIONS'])
@token_required
@admin_required
def update_post_status(post_id):
    """
    PATCH /api/admin/tuition-posts/<post_id>/status
    Update post status (e.g. 'open' or 'closed').
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    post = db.session.get(TuitionPost, post_id)
    if not post:
        return jsonify({"success": False, "error": "Tuition post not found."}), 404

    data = request.get_json() or {}
    new_status = data.get('status', '').strip().lower()

    if new_status not in ['open', 'closed']:
        return jsonify({"success": False, "error": "Invalid status value. Must be 'open' or 'closed'."}), 400

    post.status = new_status
    db.session.commit()
    return jsonify({
        "success": True,
        "message": f"Tuition post status updated to '{new_status}'.",
        "post": post.to_dict()
    }), 200


@admin_bp.route('/api/admin/tuition-posts/<int:post_id>', methods=['DELETE', 'OPTIONS'])
@token_required
@admin_required
def delete_tuition_post(post_id):
    """
    DELETE /api/admin/tuition-posts/<post_id>
    Delete an inappropriate tuition post.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    post = db.session.get(TuitionPost, post_id)
    if not post:
        return jsonify({"success": False, "error": "Tuition post not found."}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": f"Tuition post #{post_id} deleted successfully."
    }), 200
