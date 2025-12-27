
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("main.app_graph.invoke")
def test_chat_success_code(mock_invoke):
    # Simulate succesful code generation
    mock_result = {
        "generated_code": "print('Hello World')",
        "plan": "STATUS: READY\nPlan: Write code.",
        "context": ["Context 1"]
    }
    mock_invoke.return_value = mock_result
    
    payload = {"query": "Write python hello world", "history": []}
    response = client.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "print('Hello World')"
    assert data["plan"] == mock_result["plan"]

@patch("main.app_graph.invoke")
def test_chat_needs_clarification(mock_invoke):
    # Simulate INCOMPLETE plan
    mock_result = {
        "generated_code": "",
        "plan": "STATUS: INCOMPLETE\nQUESTION: Which language?",
        "context": []
    }
    mock_invoke.return_value = mock_result
    
    payload = {"query": "Write hello world", "history": []}
    response = client.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Logic in main.py: if INCOMPLETE and no code, response = plan/question
    assert "Clarification Needed" in data["response"]
    assert "Which language?" in data["response"]
