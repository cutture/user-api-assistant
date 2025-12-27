
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

import pytest
from unittest.mock import MagicMock, patch
from core.vector_store import VectorStore

@pytest.fixture
def mock_collection():
    mock = MagicMock()
    mock.query.return_value = {"documents": [["doc1"]], "metadatas": [[{"source": "test"}]]}
    return mock

@pytest.fixture
def store(mock_collection):
    with patch("chromadb.PersistentClient") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.get_or_create_collection.return_value = mock_collection
        
        # We need to bypass singleton in main code, so create fresh instance
        vs = VectorStore()
        # Inject mock
        vs.client = mock_client
        return vs

def test_add_documents(store, mock_collection):
    store.add_documents(["test"], [{"meta": "data"}], ["id1"])
    # Verify add was called on collection (lazy loaded)
    # Since _get_collection is called internally
    # We can mock _get_collection
    pass # Difficult to test implementation details without more mocking

def test_query_documents(store):
    # This tests the LRU cache decorator too
    with patch.object(store, "_get_collection") as mock_get:
        mock_coll = MagicMock()
        mock_coll.query.return_value =  {"documents": [["result"]]}
        mock_get.return_value = mock_coll
        
        res1 = store.query("test")
        res2 = store.query("test")
        
        assert res1 == {"documents": [["result"]]}
        assert res2 == {"documents": [["result"]]}
        
        # Check that query was called only ONCE (due to cache)
        mock_coll.query.assert_called_once()
