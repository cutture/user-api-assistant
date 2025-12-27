
from core.hybrid import HybridRetriever
from unittest.mock import MagicMock, patch
import pytest

# Mock Vector Store results
VECTOR_RESULTS = {
    'ids': [['id1', 'id2']],
    'documents': [['Semantic Doc about Dogs', 'Semantic Doc about Cats']],
    'metadatas': [[{'type': 'animal'}, {'type': 'animal'}]]
}

DOC_REGISTRY_DATA = {
    'documents': ['Semantic Doc about Dogs', 'Semantic Doc about Cats', 'Keyword Doc about Python Exception 0x123'],
    'ids': ['id1', 'id2', 'id3'],
    'metadatas': [{'type': 'animal'}, {'type': 'animal'}, {'type': 'tech'}]
}

@patch("core.expansion.expander")
@patch("core.cache.cache_manager")
@patch("core.hybrid.vector_store")
def test_hybrid_search(mock_vector_store, mock_cache, mock_expander):
    # 1. Setup Expander to return original query (No expansion noise for this test)
    mock_expander.expand.side_effect = lambda q: [q]
    
    # 2. Setup Cache to miss
    mock_cache.get.return_value = None
    
    # 3. Setup Vector Store
    # A. Sync Index Data
    mock_vector_store.get_all_documents.return_value = DOC_REGISTRY_DATA
    
    # B. Query Result (Semantic Search finding Animals)
    mock_vector_store.query.return_value = VECTOR_RESULTS
    
    # C. Embedding for Query (Used in MMR)
    mock_vector_store.embedding_fn.return_value = [[1.0, 0.0, 0.0]]
    
    # D. Fetch Embeddings for MMR Candidates (Used in search)
    # We need to return embeddings for id1, id2, id3
    # Let's say id3 (Python) matches query [1,0,0] perfectly.
    # id1, id2 are animals [0,1,0]
    
    mock_collection = MagicMock()
    mock_vector_store._get_collection.return_value = mock_collection
    
    def mock_get_embeddings(ids, include):
        # Return embeddings for requested IDs
        embeddings = []
        for doc_id in ids:
            if doc_id == 'id3': # Python Doc
                embeddings.append([1.0, 0.0, 0.0])
            else:
                embeddings.append([0.0, 1.0, 0.0])
        return {'ids': ids, 'embeddings': embeddings}
    
    mock_collection.get.side_effect = mock_get_embeddings

    # Initialize Retriever (triggers sync)
    retriever = HybridRetriever()
    
    assert retriever.bm25 is not None
    assert len(retriever.corpus) == 3
    
    # Test 1: Keyword Search
    # Query: "Python Exception 0x123"
    results = retriever.search("Python Exception 0x123", n_results=3)
    
    # Check that we got results
    docs = results["documents"][0]
    
    # Check content
    has_keyword_doc = any("0x123" in doc for doc in docs)
    assert has_keyword_doc, "BM25 (or MMR) failed to retrieve/retain keyword-specific document."

def test_tokenize():
    retriever = HybridRetriever() # Will fail sync if mocked poorly, but we just test static method if possible
    # Actually init calls sync. We can mock vector store again or empty it.
    
    with patch("core.hybrid.vector_store") as mvs:
        mvs.get_all_documents.return_value = {}
        r = HybridRetriever()
        tokens = r._tokenize("Hello, World!")
        assert "hello" in tokens
        assert "world" in tokens
