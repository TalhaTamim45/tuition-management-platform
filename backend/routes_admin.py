from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, TuitionPost
from schemas import RoleUpdate, BlockUpdate, StatusUpdate
from auth import require_admin

admin_router = APIRouter(prefix="/api/admin", tags=["Admin Moderation"])

@admin_router.get("/users")
def list_all_users(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.id.asc()).all()
    return {
        "success": True,
        "count": len(users),
        "users": [user.to_dict() for user in users]
    }

@admin_router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    data: RoleUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    new_role = data.role.strip().lower()
    if new_role not in ['client', 'tutor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'client', 'tutor', or 'admin'"
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )

    target_user.role = new_role
    db.commit()
    db.refresh(target_user)

    return {
        "success": True,
        "message": f"User role updated to '{new_role}' successfully.",
        "user": target_user.to_dict()
    }

@admin_router.put("/users/{user_id}/block")
def toggle_user_block(
    user_id: int,
    data: BlockUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot block their own account."
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )

    target_user.is_blocked = bool(data.is_blocked)
    db.commit()
    db.refresh(target_user)

    status_str = "blocked" if target_user.is_blocked else "unblocked"
    return {
        "success": True,
        "message": f"User has been {status_str} successfully.",
        "user": target_user.to_dict()
    }

@admin_router.get("/tuition-posts")
def list_all_tuition_posts(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    posts = db.query(TuitionPost).order_by(TuitionPost.created_at.desc()).all()
    return {
        "success": True,
        "count": len(posts),
        "posts": [post.to_dict() for post in posts]
    }

@admin_router.put("/tuition-posts/{post_id}/status")
def update_post_status(
    post_id: int,
    data: StatusUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    new_status = data.status.strip().lower()
    if new_status not in ['open', 'closed']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'open' or 'closed'"
        )

    post = db.query(TuitionPost).filter(TuitionPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition post not found"
        )

    post.status = new_status
    db.commit()
    db.refresh(post)

    return {
        "success": True,
        "message": f"Tuition post status updated to '{new_status}' successfully.",
        "post": post.to_dict()
    }

@admin_router.delete("/tuition-posts/{post_id}")
def admin_delete_tuition_post(
    post_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    post = db.query(TuitionPost).filter(TuitionPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tuition post not found"
        )

    db.delete(post)
    db.commit()

    return {
        "success": True,
        "message": f"Tuition post {post_id} deleted successfully by admin."
    }
