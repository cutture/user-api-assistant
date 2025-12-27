
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("main.vector_store")
def test_upload_text_file(mock_store):
    # Mock add_documents
    mock_store.add_documents.return_value = None
    
    filename = "test_doc.txt"
    content = b"This is a test document content."
    
    files = {"file": (filename, content, "text/plain")}
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["filename"] == filename
    assert data["chunks_added"] > 0
    
    # Verify vector store called
    mock_store.add_documents.assert_called_once()

@patch("main.vector_store")
def test_upload_json_file(mock_store):
    mock_store.add_documents.return_value = None
    
    filename = "test.json"
    content = b'{"name": "test", "value": 123}'
    
    files = {"file": (filename, content, "application/json")}
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    mock_store.add_documents.assert_called_once()
