import os
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text
from models import db, User, TuitionPost
from auth import generate_password_hash
from routes_auth import auth_bp
from routes_tuition_posts import tuition_posts_bp
from routes_admin import admin_bp

def create_app(db_uri=None):
    app = Flask(__name__)

    # Configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or f"sqlite:///{os.path.join(base_dir, 'tuition_platform.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', "tuition_platform_secret_key_cse309_assessment4")

    # CORS configuration allowing cross-origin requests from Vite frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tuition_posts_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def read_root():
        return jsonify({
            "status": "online",
            "message": "Tuition Management Platform API is running."
        })

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "Backend is running",
            "database": "Connected"
        })

    # Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    with app.app_context():
        db.create_all()
        migrate_database()
        seed_admin_user()
        seed_demo_data()

    return app

def migrate_database():
    """Safely migrate database schema and legacy user roles."""
    with db.engine.connect() as conn:
        # 1. Add missing 'phone' column if not present
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT ''"))
            conn.commit()
        except Exception:
            pass  # Column already exists

        # 2. Add missing 'is_blocked' column if not present
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_blocked BOOLEAN DEFAULT 0"))
            conn.commit()
        except Exception:
            pass  # Column already exists

    # 3. Safe Role Unification Migration: Convert legacy roles to 'client', 'tutor', 'admin'
    users = User.query.all()
    for user in users:
        current_role = (user.role or '').strip().lower()
        if current_role in ['guardian', 'student', 'student_guardian', '']:
            user.role = 'client'
        elif current_role == 'tutor':
            user.role = 'tutor'
        elif current_role == 'admin':
            user.role = 'admin'
        else:
            user.role = 'client'
    db.session.commit()

def seed_admin_user():
    """Seed initial admin account safely from environment variables or defaults."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com").strip().lower()
    admin_name = os.getenv("ADMIN_NAME", "System Admin").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123").strip()

    admin_exists = User.query.filter_by(role='admin').first()
    if not admin_exists:
        existing_by_email = User.query.filter_by(email=admin_email).first()
        if existing_by_email:
            existing_by_email.role = 'admin'
            existing_by_email.password_hash = generate_password_hash(admin_password)
        else:
            new_admin = User(
                name=admin_name,
                email=admin_email,
                phone="+8801700000000",
                password_hash=generate_password_hash(admin_password),
                role="admin",
                is_blocked=False
            )
            db.session.add(new_admin)
        db.session.commit()

def seed_demo_data():
    """Seed initial sample users and tuition posts if demo data is missing."""
    if User.query.filter_by(role='client').count() == 0:
        client = User(
            name="Fahim Ahmed (Client)",
            email="client@example.com",
            phone="+8801712345678",
            password_hash=generate_password_hash("password123"),
            role="client",
            is_blocked=False
        )
        tutor = User(
            name="Rahim Khan (Tutor)",
            email="tutor@example.com",
            phone="+8801812345678",
            password_hash=generate_password_hash("password123"),
            role="tutor",
            is_blocked=False
        )
        db.session.add_all([client, tutor])
        db.session.commit()

        # Seed sample tuition post for client
        sample_post = TuitionPost(
            user_id=client.id,
            title="Need Class 9 Higher Math & Physics Tutor",
            student_class="Class 9",
            subjects="Higher Math, Physics",
            location="Dhanmondi, Dhaka",
            monthly_salary=8000.00,
            preferred_tutor_gender="Male",
            teaching_mode="Offline",
            days_per_week=4,
            additional_notes="Looking for a patient BUET or DU tutor for home tutoring.",
            status="open"
        )
        db.session.add(sample_post)
        db.session.commit()

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
