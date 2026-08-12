from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, TuitionPost, Application
from schemas import TuitionPostCreate
from auth import get_current_user, require_client, require_tutor

tuition_posts_router = APIRouter(prefix="/api/tuition-posts", tags=["Tuition Posts"])

@tuition_posts_router.get("")
@tuition_posts_router.get("/")
def get_all_posts(
    student_class: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    query = db.query(TuitionPost)

    if student_class:
        query = query.filter(TuitionPost.student_class.ilike(f"%{student_class.strip()}%"))
    if location:
        query = query.filter(TuitionPost.location.ilike(f"%{location.strip()}%"))
    if status_filter:
        query = query.filter(TuitionPost.status == status_filter.strip().lower())
    else:
        query = query.filter(TuitionPost.status == 'open')

    posts = query.order_by(TuitionPost.created_at.desc()).all()
    return {
        "success": True,
        "count": len(posts),
        "posts": [post.to_dict() for post in posts]
    }

@tuition_posts_router.get("/my-posts")
def get_my_posts(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db)
):
    posts = db.query(TuitionPost).filter(
        TuitionPost.user_id == current_user.id
    ).order_by(TuitionPost.created_at.desc()).all()

    return {
        "success": True,
        "count": len(posts),
        "posts": [post.to_dict() for post in posts]
    }

@tuition_posts_router.post("", status_code=status.HTTP_201_CREATED)
@tuition_posts_router.post("/", status_code=status.HTTP_201_CREATED)
def create_tuition_post(
    data: TuitionPostCreate,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db)
):
    if not data.title.strip() or not data.student_class.strip() or not data.subjects.strip() or not data.location.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title, student class, subjects, and location are required."
        )

    if data.monthly_salary <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monthly salary must be greater than zero."
        )

    if data.days_per_week <= 0 or data.days_per_week > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days per week must be between 1 and 7."
        )

    new_post = TuitionPost(
        user_id=current_user.id,
        title=data.title.strip(),
        student_class=data.student_class.strip(),
        subjects=data.subjects.strip(),
        location=data.location.strip(),
        monthly_salary=float(data.monthly_salary),
        preferred_tutor_gender=(data.preferred_tutor_gender or "Any").strip(),
        teaching_mode=(data.teaching_mode or "Offline").strip(),
        days_per_week=int(data.days_per_week),
        additional_notes=(data.additional_notes or "").strip(),
        status="open"
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "success": True,
        "message": "Tuition post created successfully",
        "post": new_post.to_dict()
    }

@tuition_posts_router.get("/{post_id}")
def get_post_detail(post_id: int, db: Session = Depends(get_db)):
    post = db.query(TuitionPost).filter(TuitionPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition post not found"
        )
    return {
        "success": True,
        "post": post.to_dict()
    }

@tuition_posts_router.delete("/{post_id}")
def delete_tuition_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(TuitionPost).filter(TuitionPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition post not found"
        )

    if post.user_id != current_user.id and current_user.role.lower() != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this tuition post."
        )

    db.delete(post)
    db.commit()

    return {
        "success": True,
        "message": f"Tuition post {post_id} deleted successfully."
    }

@tuition_posts_router.post("/{post_id}/apply")
def apply_for_tuition_post(
    post_id: int,
    current_user: User = Depends(require_tutor),
    db: Session = Depends(get_db)
):
    post = db.query(TuitionPost).filter(TuitionPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition post not found"
        )

    if post.status != 'open':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This tuition post is closed for applications."
        )

    existing_app = db.query(Application).filter(
        Application.tuition_post_id == post_id,
        Application.tutor_id == current_user.id
    ).first()
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this tuition post."
        )

    new_app = Application(
        tuition_post_id=post_id,
        tutor_id=current_user.id,
        status='pending'
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return {
        "success": True,
        "message": f"Successfully applied for tuition post '{post.title}'.",
        "post_id": post_id,
        "application": new_app.to_dict()
    }

@tuition_posts_router.put("/{post_id}")
def update_tuition_post(
    post_id: int,
    data: TuitionPostCreate,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db)
):
    post = db.query(TuitionPost).filter(TuitionPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition post not found"
        )

    if post.user_id != current_user.id and current_user.role.lower() != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this tuition post."
        )

    if not data.title.strip() or not data.student_class.strip() or not data.subjects.strip() or not data.location.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title, student class, subjects, and location are required."
        )

    if data.monthly_salary <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monthly salary must be greater than zero."
        )

    if data.days_per_week <= 0 or data.days_per_week > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days per week must be between 1 and 7."
        )

    post.title = data.title.strip()
    post.student_class = data.student_class.strip()
    post.subjects = data.subjects.strip()
    post.location = data.location.strip()
    post.monthly_salary = float(data.monthly_salary)
    post.preferred_tutor_gender = (data.preferred_tutor_gender or "Any").strip()
    post.teaching_mode = (data.teaching_mode or "Offline").strip()
    post.days_per_week = int(data.days_per_week)
    post.additional_notes = (data.additional_notes or "").strip()

    db.commit()
    db.refresh(post)

    return {
        "success": True,
        "message": "Tuition post updated successfully",
        "post": post.to_dict()
    }
