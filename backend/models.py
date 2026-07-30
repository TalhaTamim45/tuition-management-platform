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
            "created_at": self.created_at.isoformat() if self.created_at else None
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
