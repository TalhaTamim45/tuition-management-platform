from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserRegister, UserLogin, UserProfileUpdate
from auth import generate_token, generate_password_hash, check_password_hash, get_current_user

auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    name = data.name.strip()
    email = data.email.strip().lower()
    password = data.password.strip()
    phone = (data.phone or "").strip()
    raw_role = (data.role or "client").strip().lower()

    if not name or not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name, email, and password are required."
        )

    if raw_role not in ['client', 'tutor']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account role"
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    hashed_pw = generate_password_hash(password)
    new_user = User(
        name=name,
        email=email,
        phone=phone,
        password_hash=hashed_pw,
        role=raw_role,
        is_blocked=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = generate_token(new_user.id)
    return {
        "success": True,
        "message": "User registered successfully",
        "token": token,
        "user": new_user.to_dict()
    }

@auth_router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    password = data.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required."
        )

    user = db.query(User).filter(User.email == email).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended by an administrator."
        )

    token = generate_token(user.id)
    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    }

@auth_router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "user": current_user.to_dict()
    }

@auth_router.put("/profile")
def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    name = data.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required."
        )

    current_user.name = name
    current_user.phone = (data.phone or "").strip()
    current_user.education = (data.education or "").strip()
    current_user.institution = (data.institution or "").strip()
    current_user.subjects = (data.subjects or "").strip()
    current_user.experience = (data.experience or "").strip()
    current_user.salary_expectation = float(data.salary_expectation or 0.0)
    current_user.address = (data.address or "").strip()

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Profile updated successfully.",
        "user": current_user.to_dict()
    }
