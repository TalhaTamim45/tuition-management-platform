import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import User, TuitionPost
from auth import generate_password_hash, generate_token

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_tuition_posts.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_database():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    client_user = User(
        name="Client User",
        email="client_test@example.com",
        phone="+8801711111111",
        password_hash=generate_password_hash("password123"),
        role="client",
        is_blocked=False
    )
    tutor_user = User(
        name="Tutor User",
        email="tutor_test@example.com",
        phone="+8801811111111",
        password_hash=generate_password_hash("password123"),
        role="tutor",
        is_blocked=False
    )
    db.add_all([client_user, tutor_user])
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

client = TestClient(app)

def test_1_successful_tuition_post_creation():
    db = TestingSessionLocal()
    client_user = db.query(User).filter(User.email == "client_test@example.com").first()
    token = generate_token(client_user.id)
    db.close()

    payload = {
        "title": "Need Class 10 Physics & Chemistry Tutor",
        "student_class": "Class 10",
        "subjects": "Physics, Chemistry",
        "location": "Gulshan, Dhaka",
        "monthly_salary": 9000.0,
        "preferred_tutor_gender": "Female",
        "teaching_mode": "Offline",
        "days_per_week": 3,
        "additional_notes": "Needs experienced tutor."
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/tuition-posts", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["post"]["title"] == "Need Class 10 Physics & Chemistry Tutor"

def test_2_unauthorized_post_creation_by_tutor():
    db = TestingSessionLocal()
    tutor_user = db.query(User).filter(User.email == "tutor_test@example.com").first()
    token = generate_token(tutor_user.id)
    db.close()

    payload = {
        "title": "Invalid Post by Tutor",
        "student_class": "Class 8",
        "subjects": "General Math",
        "location": "Banani, Dhaka",
        "monthly_salary": 5000.0,
        "days_per_week": 3
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/tuition-posts", json=payload, headers=headers)
    assert response.status_code == 403

def test_3_public_post_listing():
    response = client.get("/api/tuition-posts")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "posts" in data

def test_4_tutor_apply_for_post():
    db = TestingSessionLocal()
    client_user = db.query(User).filter(User.email == "client_test@example.com").first()
    tutor_user = db.query(User).filter(User.email == "tutor_test@example.com").first()
    client_token = generate_token(client_user.id)
    tutor_token = generate_token(tutor_user.id)
    db.close()

    payload = {
        "title": "Need ICT Tutor",
        "student_class": "HSC",
        "subjects": "ICT",
        "location": "Mirpur, Dhaka",
        "monthly_salary": 6000.0,
        "days_per_week": 3
    }
    create_res = client.post("/api/tuition-posts", json=payload, headers={"Authorization": f"Bearer {client_token}"})
    post_id = create_res.json()["post"]["id"]

    apply_res = client.post(f"/api/tuition-posts/{post_id}/apply", headers={"Authorization": f"Bearer {tutor_token}"})
    assert apply_res.status_code == 200
    apply_data = apply_res.json()
    assert apply_data["success"] is True
    assert apply_data["post_id"] == post_id
