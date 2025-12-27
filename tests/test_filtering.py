
import pytest
from core.filtering import filter_manager
from core.hybrid import HybridRetriever
from unittest.mock import MagicMock, patch

def test_filter_parsing_simple():
    query = "login issues type:guide"
    clean, filters = filter_manager.parse_query(query)
    assert clean == "login issues"
    assert filters == {"type": "guide"}

def test_filter_parsing_multiple():
    query = "source:manual auth error type:guide"
    clean, filters = filter_manager.parse_query(query)
    assert clean == "auth error"
    assert filters == {"source": "manual", "type": "guide"}

def test_filter_parsing_no_filters():
    query = "just a query"
    clean, filters = filter_manager.parse_query(query)
    assert clean == "just a query"
    assert filters == {}

def test_filter_parsing_special_chars():
    query = "error code:404 project:api-v2"
    clean, filters = filter_manager.parse_query(query)
    assert clean == "error"
    assert filters == {"code": "404", "project": "api-v2"}

@patch("core.hybrid.vector_store")
@patch("core.cache.cache_manager")
@patch("core.expansion.expander")
def test_hybrid_search_with_filters(mock_expander, mock_cache, mock_vector_store):
    # Setup
    mock_expander.expand.side_effect = lambda q: [q]
    mock_cache.get.return_value = None
    
    # Vector store setup with embeddings
    mock_vector_store.embedding_fn.return_value = [[1, 0]]
    # Mocking retrieval to just return empty so we check call args
    mock_vector_store.query.return_value = {"ids": [], "documents": [], "metadatas": []}
    mock_vector_store.get_all_documents.return_value = {"documents": [], "ids": [], "metadatas": []}
    mock_vector_store._get_collection.return_value.get.return_value = {'ids':[], 'embeddings':[]}

    retriever = HybridRetriever()
    
    # Execute Search with Filters in Query
    retriever.search("test query type:guide")
    
    # Verify Vector Store was called with correct filter
    args, kwargs = mock_vector_store.query.call_args
    assert kwargs.get("where") == {"type": "guide"}
    # Verify query text passed was cleaned "test query" (args[0] or kwargs['query'])
    # Since expander returns [q], the loop calls vector_store.query(q)
    assert args[0] == "test query"
