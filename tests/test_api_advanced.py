
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("core.hybrid.hybrid_retriever.search")
@patch("core.hybrid.hybrid_retriever.doc_registry")
def test_search_endpoint_basic(mock_registry, mock_search):
    # Setup Mock Returns
    mock_search.return_value = {
        "documents": [["Doc A", "Doc B"]],
        "ids": [["1", "2"]]
    }
    
    # Mock Registry Lookup for Metadata
    # Registry is dict: {0: {'id': '1', ...}, 1: {'id': '2', ...}}
    # But endpoint iterates .values()
    mock_registry.values.return_value = [
        {"id": "1", "content": "Doc A", "metadata": {"source": "manual"}},
        {"id": "2", "content": "Doc B", "metadata": {"type": "guide"}}
    ]
    
    payload = {
        "query": "test query",
        "limit": 2
    }
    
    response = client.post("/v1/search", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test query"
    assert len(data["results"]) == 2
    assert data["results"][0]["content"] == "Doc A"
    assert data["results"][0]["metadata"] == {"source": "manual"}

def test_search_endpoint_with_filters():
    with patch("core.hybrid.hybrid_retriever.search") as mock_search:
        mock_search.return_value = {"documents": [[]], "ids": [[]]}
        
        payload = {
            "query": "filtered query",
            "filters": {"type": "guide"}
        }
        
        client.post("/v1/search", json=payload)
        
        # Check that filters were passed to search logic
        args, kwargs = mock_search.call_args
        assert kwargs["filters"] == {"type": "guide"}
        assert kwargs["query"] == "filtered query"
