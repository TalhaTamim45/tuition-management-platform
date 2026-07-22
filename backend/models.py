from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Guardian') # Guardian, Student, Tutor, Admin
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship with TuitionPost
    tuition_posts = db.relationship('TuitionPost', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class TuitionPost(db.Model):
    __tablename__ = 'tuition_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    student_class = db.Column(db.String(50), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    monthly_salary = db.Column(db.Float, nullable=False)
    preferred_tutor_gender = db.Column(db.String(20), default='Any')
    teaching_mode = db.Column(db.String(20), nullable=False, default='Offline') # Online, Offline
    days_per_week = db.Column(db.Integer, nullable=False)
    additional_notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='open') # open, closed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "student_class": self.student_class,
            "subjects": self.subjects,
            "location": self.location,
            "monthly_salary": self.monthly_salary,
            "preferred_tutor_gender": self.preferred_tutor_gender,
            "teaching_mode": self.teaching_mode,
            "days_per_week": self.days_per_week,
            "additional_notes": self.additional_notes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
