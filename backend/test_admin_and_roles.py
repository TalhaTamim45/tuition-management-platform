import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import User, TuitionPost
from auth import generate_password_hash, generate_token

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_admin.db")
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

    admin_user = User(
        name="Admin User",
        email="admin_test@example.com",
        phone="+8801700000000",
        password_hash=generate_password_hash("admin123"),
        role="admin",
        is_blocked=False
    )
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
    db.add_all([admin_user, client_user, tutor_user])
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

def test_1_admin_list_users():
    db = TestingSessionLocal()
    admin_user = db.query(User).filter(User.email == "admin_test@example.com").first()
    admin_token = generate_token(admin_user.id)
    db.close()

    response = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["users"]) >= 3

def test_2_non_admin_cannot_access_admin_endpoints():
    db = TestingSessionLocal()
    client_user = db.query(User).filter(User.email == "client_test@example.com").first()
    client_token = generate_token(client_user.id)
    db.close()

    response = client.get("/api/admin/users", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 403

def test_3_admin_update_user_role():
    db = TestingSessionLocal()
    admin_user = db.query(User).filter(User.email == "admin_test@example.com").first()
    client_user = db.query(User).filter(User.email == "client_test@example.com").first()
    admin_token = generate_token(admin_user.id)
    client_id = client_user.id
    db.close()

    response = client.put(
        f"/api/admin/users/{client_id}/role",
        json={"role": "tutor"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["role"] == "tutor"

def test_4_admin_toggle_block_user():
    db = TestingSessionLocal()
    admin_user = db.query(User).filter(User.email == "admin_test@example.com").first()
    tutor_user = db.query(User).filter(User.email == "tutor_test@example.com").first()
    admin_token = generate_token(admin_user.id)
    tutor_id = tutor_user.id
    db.close()

    response = client.put(
        f"/api/admin/users/{tutor_id}/block",
        json={"is_blocked": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["is_blocked"] is True

    # Blocked user attempt to access authenticated endpoint
    tutor_token = generate_token(tutor_id)
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tutor_token}"})
    assert me_res.status_code == 403
