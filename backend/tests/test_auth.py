import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app import models

client = TestClient(app)


# Automatically clear users table before and after each test
@pytest.fixture(autouse=True)
def clear_users():
    db: Session = next(get_db())
    db.query(models.User).delete()
    db.commit()
    yield
    db.query(models.User).delete()
    db.commit()


@pytest.fixture
def user_payload():
    return {"email": "user@example.com", "password": "P@ssw0rd!"}


def test_register_login_me_refresh_logout(user_payload):
    # Register with role = advisor
    r = client.post("/auth/register", json={**user_payload, "role": "advisor"})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == user_payload["email"]
    assert data["role"] == "advisor"

    # Login
    r = client.post("/auth/login", json=user_payload)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    access = tokens["access_token"]
    refresh = tokens["refresh_token"]

    # Me
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == user_payload["email"]
    assert data["role"] == "advisor"

    # Refresh
    r = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    tokens2 = r.json()
    assert "access_token" in tokens2
    assert "refresh_token" in tokens2

    # Logout
    r = client.post("/auth/logout", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    assert r.json()["message"] == "Logged out"


def test_role_based_access():
    # Register an admin user
    r = client.post(
        "/auth/register",
        json={"email": "admin@example.com", "password": "Secret123!", "role": "admin"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "admin@example.com"
    assert data["role"] == "admin"

    # Login
    r = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "Secret123!"},
    )
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens

    access = tokens["access_token"]

    # Me (should include role)
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "admin@example.com"
    assert data["role"] == "admin"
