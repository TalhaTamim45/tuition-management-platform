from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True, default='')
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='client')  # client, tutor, admin
    is_blocked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Profile details (specifically for Tutors, but accessible/generic)
    education = Column(String(200), nullable=True, default='')
    institution = Column(String(200), nullable=True, default='')
    subjects = Column(String(255), nullable=True, default='')
    experience = Column(String(100), nullable=True, default='')
    salary_expectation = Column(Float, nullable=True, default=0.0)
    address = Column(String(200), nullable=True, default='')

    # Relationship with TuitionPost
    tuition_posts = relationship('TuitionPost', back_populates='user', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone or '',
            "role": self.role.lower() if self.role else 'client',
            "is_blocked": bool(self.is_blocked),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "education": self.education or '',
            "institution": self.institution or '',
            "subjects": self.subjects or '',
            "experience": self.experience or '',
            "salary_expectation": float(self.salary_expectation or 0.0),
            "address": self.address or ''
        }

class TuitionPost(Base):
    __tablename__ = 'tuition_posts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(200), nullable=False)
    student_class = Column(String(50), nullable=False)
    subjects = Column(String(255), nullable=False)
    location = Column(String(150), nullable=False)
    monthly_salary = Column(Float, nullable=False)
    preferred_tutor_gender = Column(String(20), default='Any')
    teaching_mode = Column(String(20), nullable=False, default='Offline')  # Online, Offline
    days_per_week = Column(Integer, nullable=False)
    additional_notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='open')  # open, closed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship with User
    user = relationship('User', back_populates='tuition_posts')
    
    # Relationship with Application
    applications = relationship('Application', back_populates='tuition_post', cascade="all, delete-orphan")

    def to_dict(self):
        creator_name = self.user.name if self.user else "Unknown Client"
        return {
            "id": self.id,
            "user_id": self.user_id,
            "client_name": creator_name,
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

class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, index=True)
    tuition_post_id = Column(Integer, ForeignKey('tuition_posts.id', ondelete='CASCADE'), nullable=False)
    tutor_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(20), nullable=False, default='pending')  # pending, accepted, rejected
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    tuition_post = relationship('TuitionPost', back_populates='applications')
    tutor = relationship('User')

    def to_dict(self):
        tutor_info = self.tutor.to_dict() if self.tutor else {}
        return {
            "id": self.id,
            "tuition_post_id": self.tuition_post_id,
            "tutor_id": self.tutor_id,
            "status": self.status,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "tutor_name": tutor_info.get("name", "Unknown Tutor"),
            "tutor_email": tutor_info.get("email", ""),
            "tutor_phone": tutor_info.get("phone", ""),
            "tutor_education": tutor_info.get("education", ""),
            "tutor_institution": tutor_info.get("institution", ""),
            "tutor_subjects": tutor_info.get("subjects", ""),
            "tutor_experience": tutor_info.get("experience", ""),
            "tutor_salary_expectation": tutor_info.get("salary_expectation", 0.0)
        }
