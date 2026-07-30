import os
import datetime
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models import User

SECRET_KEY = os.getenv("SECRET_KEY", "tuition_platform_secret_key_cse309_assessment4")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer(auto_error=False)

def generate_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception:
        # Fallback hashing if bcrypt environment issue occurs
        import hashlib
        return "sha256$" + hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password_hash(pw_hash: str, password: str) -> bool:
    if pw_hash.startswith("sha256$"):
        import hashlib
        expected = "sha256$" + hashlib.sha256(password.encode('utf-8')).hexdigest()
        return pw_hash == expected
    try:
        return pwd_context.verify(password, pw_hash)
    except Exception:
        return False

def generate_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing or invalid"
        )
    
    token = credentials.credentials
    data = decode_token(token)
    if not data or 'user_id' not in data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )
    
    user = db.query(User).filter(User.id == data['user_id']).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended by an administrator."
        )
    
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.lower() != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def require_tutor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.lower() != 'tutor':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tutor privileges required"
        )
    return current_user

def require_client(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.lower() != 'client':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client privileges required"
        )
    return current_user
