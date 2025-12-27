
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.sessions import session_manager

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Clear sessions before each test
    session_manager._sessions = {}
    yield

def test_create_session():
    response = client.post("/sessions/", json={"user_id": "test_user"})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user"
    assert "id" in data
    assert session_manager.get_session(data["id"]) is not None

def test_list_sessions():
    session_manager.create_session("user1")
    session_manager.create_session("user2")
    
    response = client.get("/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Filter
    response = client.get("/sessions/?user_id=user1")
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == "user1"

def test_session_history():
    s = session_manager.create_session("chatty_user")
    session_manager.add_message(s.id, "user", "Hello")
    session_manager.add_message(s.id, "assistant", "Hi there")
    
    response = client.get(f"/sessions/{s.id}/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"

# We skip testing the /chat endpoint fully because it invokes the real Agent Graph
# which requires LLM keys and time. We assume integration tests cover that layer.
