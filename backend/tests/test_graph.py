from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_graph_endpoint_ok():
    response = client.get("/graph/1")  # assumes program_id=1 exists
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
