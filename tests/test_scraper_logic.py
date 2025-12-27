
import pytest
from unittest.mock import patch, MagicMock
from agent.nodes import retrieve_node
from langchain_core.messages import HumanMessage

@patch("agent.nodes.requests.get")
@patch("agent.nodes.vector_store")
def test_scraper_success(mock_vector_store, mock_get):
    # Mock successful HTML response
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Content must be > 1000 chars to pass "is_too_short" check
    long_content = "Test Content " * 100
    mock_response.content = f"<html><body><h1>Test Header</h1><p>{long_content}</p></body></html>".encode("utf-8")
    mock_get.return_value = mock_response
    
    # Mock Vector Store to return empty so we rely on scrape
    mock_vector_store.query.return_value = {}
    
    state = {
        "messages": [HumanMessage(content="Check http://example.com for info.")],
        "context": []
    }
    
    result = retrieve_node(state)
    
    # Verify Scrape Happened
    # Check simple call
    mock_get.assert_called()
    args, kwargs = mock_get.call_args
    assert args[0] == "http://example.com"
    assert kwargs["timeout"] == 15
    assert "User-Agent" in kwargs["headers"]
    
    assert "context" in result
    ctx = result["context"]
    # Check that context contains scraped content
    # It appends "Source URL: ... \n Content: ..."
    found = False
    for doc in ctx:
        if "Test Header" in doc:
            found = True
            break
    assert found, "Scraped content not found in context"

@patch("agent.nodes.requests.get")
@patch("agent.nodes.vector_store")
def test_scraper_failure(mock_vector_store, mock_get):
    # Mock failure
    mock_get.side_effect = Exception("Connection Failed")
    mock_vector_store.query.return_value = {}
    
    state = {
        "messages": [HumanMessage(content="Check http://bad-url.com")],
        "context": []
    }
    
    result = retrieve_node(state)
    
    assert "context" in result
    ctx = result["context"]
    # Should contain error message
    found = False
    for doc in ctx:
        if "Error: Connection Failed" in doc:
            found = True
            break
    assert found, "Error message not found in context"
