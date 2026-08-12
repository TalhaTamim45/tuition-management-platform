from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, TuitionPost, Application
from schemas import ApplicationStatusUpdate
from auth import get_current_user, require_tutor, require_client

applications_router = APIRouter(prefix="/api", tags=["Applications"])

@applications_router.get("/tuition-posts/{post_id}/applications")
def get_post_applications(
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
    
    # Authorized if current user is the client who posted it OR is an admin
    if post.user_id != current_user.id and current_user.role.lower() != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view applications for this tuition post."
        )
        
    apps = db.query(Application).filter(Application.tuition_post_id == post_id).order_by(Application.applied_at.desc()).all()
    return {
        "success": True,
        "count": len(apps),
        "applications": [app.to_dict() for app in apps]
    }

@applications_router.put("/applications/{application_id}/status")
def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_status = data.status.strip().lower()
    if new_status not in ['pending', 'accepted', 'rejected']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'pending', 'accepted', or 'rejected'."
        )
        
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
        
    post = db.query(TuitionPost).filter(TuitionPost.id == app_record.tuition_post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated tuition post not found"
        )
        
    # Authorized if current user is the client who posted the tuition job OR admin
    if post.user_id != current_user.id and current_user.role.lower() != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to moderate applications for this tuition post."
        )
        
    app_record.status = new_status
    db.commit()
    db.refresh(app_record)
    
    return {
        "success": True,
        "message": f"Application status updated to '{new_status}' successfully.",
        "application": app_record.to_dict()
    }

@applications_router.get("/applications/my-applications")
def get_my_applications(
    current_user: User = Depends(require_tutor),
    db: Session = Depends(get_db)
):
    apps = db.query(Application).filter(Application.tutor_id == current_user.id).order_by(Application.applied_at.desc()).all()
    
    # Attach tuition post details to the application dictionary representation
    app_list = []
    for app in apps:
        app_dict = app.to_dict()
        post = app.tuition_post
        app_dict["tuition_post"] = {
            "id": post.id,
            "title": post.title,
            "student_class": post.student_class,
            "subjects": post.subjects,
            "location": post.location,
            "monthly_salary": post.monthly_salary,
            "teaching_mode": post.teaching_mode,
            "days_per_week": post.days_per_week,
            "status": post.status
        } if post else None
        app_list.append(app_dict)
        
    return {
        "success": True,
        "count": len(apps),
        "applications": app_list
    }
