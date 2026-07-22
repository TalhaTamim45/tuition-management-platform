from flask import Blueprint, request, jsonify, g
from models import db, TuitionPost
from auth import token_required

tuition_posts_bp = Blueprint('tuition_posts', __name__)

@tuition_posts_bp.route('/api/tuition-posts', methods=['POST', 'OPTIONS'])
@token_required
def create_tuition_post():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    """
    POST /api/tuition-posts
    Create a new tuition post.
    Access restricted to logged-in Guardians or Students.
    """
    current_user = g.current_user

    # Authorization Check: Only Guardians and Students can post tuition jobs
    if current_user.role not in ['Guardian', 'Student']:
        return jsonify({
            "success": False,
            "error": f"Role '{current_user.role}' is not authorized to create tuition posts. Only Guardians or Students can post."
        }), 403

    data = request.get_json() or {}

    # Extract fields
    title = data.get('title', '')
    student_class = data.get('student_class', '')
    subjects = data.get('subjects', '')
    location = data.get('location', '')
    monthly_salary = data.get('monthly_salary')
    preferred_tutor_gender = data.get('preferred_tutor_gender', 'Any')
    teaching_mode = data.get('teaching_mode', '')
    days_per_week = data.get('days_per_week')
    additional_notes = data.get('additional_notes', '')

    # Validation errors map to report all field validation issues
    errors = {}

    # 1. Title validation
    if not title or not str(title).strip():
        errors['title'] = "Title is required."

    # 2. Student class validation
    if not student_class or not str(student_class).strip():
        errors['student_class'] = "Student class is required."

    # 3. Subjects validation
    if not subjects or not str(subjects).strip():
        errors['subjects'] = "Subjects are required."

    # 4. Location validation
    if not location or not str(location).strip():
        errors['location'] = "Location is required."

    # 5. Monthly salary validation
    if monthly_salary is None:
        errors['monthly_salary'] = "Monthly salary is required."
    else:
        try:
            val = float(monthly_salary)
            if val <= 0:
                errors['monthly_salary'] = "Monthly salary must be a positive number."
        except (ValueError, TypeError):
            errors['monthly_salary'] = "Monthly salary must be a valid numeric value."

    # 6. Teaching mode validation
    valid_modes = ['Online', 'Offline']
    if not teaching_mode or teaching_mode not in valid_modes:
        errors['teaching_mode'] = f"Teaching mode must be either 'Online' or 'Offline'."

    # 7. Days per week validation
    if days_per_week is None:
        errors['days_per_week'] = "Days per week is required."
    else:
        try:
            days_val = int(days_per_week)
            if days_val < 1 or days_val > 7:
                errors['days_per_week'] = "Days per week must be between 1 and 7."
        except (ValueError, TypeError):
            errors['days_per_week'] = "Days per week must be an integer between 1 and 7."

    # If any validation errors exist, return 400 Bad Request
    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": errors
        }), 400

    # Sanitize and prepare data
    preferred_tutor_gender = str(preferred_tutor_gender).strip()
    if preferred_tutor_gender not in ['Male', 'Female', 'Any']:
        preferred_tutor_gender = 'Any'

    # Create new TuitionPost database record
    new_post = TuitionPost(
        user_id=current_user.id,
        title=str(title).strip(),
        student_class=str(student_class).strip(),
        subjects=str(subjects).strip(),
        location=str(location).strip(),
        monthly_salary=float(monthly_salary),
        preferred_tutor_gender=preferred_tutor_gender,
        teaching_mode=teaching_mode,
        days_per_week=int(days_per_week),
        additional_notes=str(additional_notes).strip() if additional_notes else "",
        status="open"  # Default status is 'open'
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Tuition post created successfully.",
        "post": new_post.to_dict()
    }), 201


@tuition_posts_bp.route('/api/tuition-posts/my-posts', methods=['GET', 'OPTIONS'])
@token_required
def get_my_tuition_posts():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    """
    GET /api/tuition-posts/my-posts
    Retrieve all tuition posts created by the logged-in user.
    """
    current_user = g.current_user
    posts = TuitionPost.query.filter_by(user_id=current_user.id).order_by(TuitionPost.created_at.desc()).all()
    
    return jsonify({
        "success": True,
        "count": len(posts),
        "posts": [post.to_dict() for post in posts]
    }), 200


@tuition_posts_bp.route('/api/tuition-posts', methods=['GET'])
def get_all_tuition_posts():
    """
    GET /api/tuition-posts
    Public endpoint: Get all tuition posts available.
    """
    posts = TuitionPost.query.order_by(TuitionPost.created_at.desc()).all()
    return jsonify({
        "success": True,
        "count": len(posts),
        "posts": [post.to_dict() for post in posts]
    }), 200
