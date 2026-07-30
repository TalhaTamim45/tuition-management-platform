import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import User, TuitionPost
from auth import generate_password_hash
from routes_auth import auth_router
from routes_tuition_posts import tuition_posts_router
from routes_admin import admin_router

def seed_admin_user(db):
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com").strip().lower()
    admin_name = os.getenv("ADMIN_NAME", "System Admin").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123").strip()

    admin_exists = db.query(User).filter(User.role == 'admin').first()
    if not admin_exists:
        existing_by_email = db.query(User).filter(User.email == admin_email).first()
        if existing_by_email:
            existing_by_email.role = 'admin'
            existing_by_email.password_hash = generate_password_hash(admin_password)
        else:
            new_admin = User(
                name=admin_name,
                email=admin_email,
                phone="+8801700000000",
                password_hash=generate_password_hash(admin_password),
                role="admin",
                is_blocked=False
            )
            db.add(new_admin)
        db.commit()

def seed_demo_data(db):
    if db.query(User).filter(User.role == 'client').count() == 0:
        client = User(
            name="Fahim Ahmed (Client)",
            email="client@example.com",
            phone="+8801712345678",
            password_hash=generate_password_hash("password123"),
            role="client",
            is_blocked=False
        )
        tutor = User(
            name="Rahim Khan (Tutor)",
            email="tutor@example.com",
            phone="+8801812345678",
            password_hash=generate_password_hash("password123"),
            role="tutor",
            is_blocked=False
        )
        db.add_all([client, tutor])
        db.commit()

        sample_post = TuitionPost(
            user_id=client.id,
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
        db.add(sample_post)
        db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup database creation and seeding
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin_user(db)
        seed_demo_data(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Tuition Management Platform API",
    version="1.0.0",
    description="FastAPI Backend for CSE309 Tuition Management Platform",
    lifespan=lifespan
)

# Enable CORS for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(tuition_posts_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Tuition Management Platform FastAPI Backend is running.",
        "docs": "http://localhost:5000/docs"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "Backend is running",
        "framework": "FastAPI",
        "database": "Connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
