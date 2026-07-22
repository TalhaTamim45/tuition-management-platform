import os
from flask import Flask, jsonify
from flask_cors import CORS
from models import db, User, TuitionPost
from auth import generate_password_hash
from routes_auth import auth_bp
from routes_tuition_posts import tuition_posts_bp

def create_app(db_uri=None):
    app = Flask(__name__)
    
    # Configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or f"sqlite:///{os.path.join(base_dir, 'tuition_platform.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "tuition_platform_secret_key_cse309_assessment4"

    # CORS configuration allowing cross-origin requests from Vite frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tuition_posts_bp)

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
        seed_demo_data()

    return app

def seed_demo_data():
    """Seed initial sample users and tuition posts if database is empty."""
    if User.query.count() == 0:
        guardian = User(
            name="Fahim Ahmed (Guardian)",
            email="guardian@example.com",
            password_hash=generate_password_hash("password123"),
            role="Guardian"
        )
        student = User(
            name="Tanvir Hossain (Student)",
            email="student@example.com",
            password_hash=generate_password_hash("password123"),
            role="Student"
        )
        tutor = User(
            name="Rahim Khan (Tutor)",
            email="tutor@example.com",
            password_hash=generate_password_hash("password123"),
            role="Tutor"
        )
        db.session.add_all([guardian, student, tutor])
        db.session.commit()

        # Seed sample tuition post for guardian
        sample_post = TuitionPost(
            user_id=guardian.id,
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
