# backend/tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app  # your FastAPI() is here
from backend.db import Base, get_db  # adjust import paths if different

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

# For SQLite we need this connect arg; Postgres does not need it.
connect_args = {"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create/drop schema once per test session
@pytest.fixture(scope="session", autouse=True)
def _create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Override FastAPI dependency to use the test session
def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = _override_get_db

# Client for tests
@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
