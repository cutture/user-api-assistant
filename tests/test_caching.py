
import pytest
from unittest.mock import patch, MagicMock
from core.cache import CacheManager
import numpy as np

# Mock vector store for caching tests
@patch("core.cache.vector_store")
def test_exact_cache(mock_vector_store):
    manager = CacheManager()
    
    query = "exact match"
    result = {"documents": ["doc1"], "ids": ["id1"]}
    
    # 1. Miss
    assert manager.get(query) is None
    
    # 2. Set
    # Need to mock embedding fn because set() calls it for semantic cache
    mock_vector_store.embedding_fn.return_value = [[0.1, 0.2, 0.3]]
    manager.set(query, result)
    
    # 3. Hit
    hit = manager.get(query)
    assert hit == result
    assert hit["documents"] == ["doc1"]

@patch("core.cache.vector_store")
def test_semantic_cache_hit(mock_vector_store):
    manager = CacheManager()
    
    # Original query stored
    q1 = "How to python"
    vec1 = [1.0, 0.0, 0.0]
    res1 = {"doc": "python guide"}
    
    mock_vector_store.embedding_fn.return_value = [vec1]
    manager.set(q1, res1)
    
    # Similar query (should hit semantic cache)
    q2 = "How do I python"
    vec2 = [0.98, 0.0, 0.0] # High cosine similarity
    
    mock_vector_store.embedding_fn.return_value = [vec2]
    
    hit = manager.get(q2)
    assert hit is not None
    assert hit == res1

@patch("core.cache.vector_store")
def test_semantic_cache_miss(mock_vector_store):
    manager = CacheManager()
    
    # Original query stored
    q1 = "How to python"
    vec1 = [1.0, 0.0, 0.0]
    res1 = {"doc": "python guide"}
    
    mock_vector_store.embedding_fn.return_value = [vec1]
    manager.set(q1, res1)
    
    # Dissimilar query (should miss)
    q2 = "How to cook"
    vec2 = [0.0, 1.0, 0.0] # 0 similarity
    
    mock_vector_store.embedding_fn.return_value = [vec2]
    
    hit = manager.get(q2)
    assert hit is None
