from typing import Optional, List
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = ""
    role: Optional[str] = "client"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = ""
    role: str
    is_blocked: bool
    created_at: Optional[str] = None

class TuitionPostCreate(BaseModel):
    title: str
    student_class: str
    subjects: str
    location: str
    monthly_salary: float
    preferred_tutor_gender: Optional[str] = "Any"
    teaching_mode: Optional[str] = "Offline"
    days_per_week: int
    additional_notes: Optional[str] = ""

class TuitionPostResponse(BaseModel):
    id: int
    user_id: int
    client_name: str
    title: str
    student_class: str
    subjects: str
    location: str
    monthly_salary: float
    preferred_tutor_gender: str
    teaching_mode: str
    days_per_week: int
    additional_notes: Optional[str] = ""
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class RoleUpdate(BaseModel):
    role: str

class BlockUpdate(BaseModel):
    is_blocked: bool

class StatusUpdate(BaseModel):
    status: str
