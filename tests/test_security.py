
from fastapi.testclient import TestClient
from main import app, app_graph
from unittest.mock import patch
import pytest

client = TestClient(app)

def test_xss_sanitization():
    """
    Verify that HTML/Script tags are stripped from input.
    """
    # Patch the graph invocation on the content object
    with patch.object(app_graph, "invoke") as mock_invoke:
        mock_invoke.return_value = {
            "generated_code": "print('clean')",
            "plan": "Clean Plan",
            "context": []
        }
        
        # Attack Payload
        xss_payload = "<script>alert('XSS')</script>Hello"
        
        payload = {"query": xss_payload, "history": []}
        response = client.post("/chat", json=payload)
        
        if response.status_code != 200:
            print(f"Failed Response: {response.text}")
            
        assert response.status_code == 200
        
        # Verify call args
        args, _ = mock_invoke.call_args
        inputs = args[0]
        last_msg = inputs["messages"][-1].content
        
        # Bleach strips tags (<script>), keeping content (alert('XSS'))
        assert "<script>" not in last_msg
        assert "Hello" in last_msg

def test_rate_limiting():
    """
    Verify that exceeding the rate limit returns 429.
    Limit for /health is 5/minute.
    """
    # Hit until blocked (Max 10 tries)
    blocked = False
    for i in range(10):
        res = client.get("/health")
        if res.status_code == 429:
            blocked = True
            break
            
    assert blocked, "Did not hit rate limit after 10 requests"
