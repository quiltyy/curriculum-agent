import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Force SQLite for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///" + os.path.join(tempfile.gettempdir(), "test_auth.db"))
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.main import app
from app.database import Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture
def user_payload():
    return {"email": "user@example.com", "password": "P@ssw0rd!"}

def test_register_login_me_refresh_logout(user_payload):
    # Register
    r = client.post("/auth/register", json=user_payload)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == user_payload["email"]

    # Login
    r = client.post("/auth/login", json=user_payload)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    # Me
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == user_payload["email"]

    # Refresh
    r = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    new_tokens = r.json()
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # Logout
    headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    r = client.post("/auth/logout", headers=headers)
    assert r.status_code == 200

    # Old token should be invalid
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 401
