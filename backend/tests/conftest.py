import sys, os
import pytest
from fastapi.testclient import TestClient

# --- Safety net: make sure repo root is on sys.path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app


@pytest.fixture()
def client():
    """FastAPI test client that uses the real app + real DB settings."""
    with TestClient(app) as c:
        yield c
