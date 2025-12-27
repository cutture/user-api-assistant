from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_health_check_ok():
    # Mock vector_store heartbeat
    with patch("backend.main.vector_store.client.heartbeat") as mock_hearbeat:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_health_check_fail():
    # Mock vector_store failure
    with patch("backend.main.vector_store.client.heartbeat", side_effect=Exception("DB Down")):
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json()["status"] == "degraded"

def test_postman_export():
    payload = {
        "plan": "Step 1: Get Pets",
        "code": "import requests\nrequests.get('https://api.petstore.io/pets')"
    }
    response = client.post("/export/postman", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert data["info"]["name"] == "API Assistant Generated Collection"
    assert len(data["item"]) > 0
