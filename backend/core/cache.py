
from cachetools import TTLCache
from typing import Dict, Any, Optional
import numpy as np
from core.vector_store import store as vector_store

class CacheManager:
    def __init__(self):
        # 1. Exact Match Cache (TTL = 1 hour, Max 1000 items)
        self.exact_cache = TTLCache(maxsize=1000, ttl=3600)
        
        # 2. Semantic Cache (List of {embedding, result})
        # Simple in-memory scan for now. In prod, use Redis/Chroma dedicated collection.
        self.semantic_cache = [] 
        self.semantic_threshold = 0.95
        self.max_semantic_size = 500

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        # A. Check Exact Cache
        if query in self.exact_cache:
            print("⚡ Exact Cache Hit")
            return self.exact_cache[query]
            
        # B. Check Semantic Cache
        query_embedding = vector_store.embedding_fn([query])[0]
        
        best_score = -1
        best_result = None
        
        for item in self.semantic_cache:
            score = self._cosine_similarity(query_embedding, item['embedding'])
            if score > best_score:
                best_score = score
                best_result = item['result']
        
        if best_score > self.semantic_threshold:
            print(f"🧠 Semantic Cache Hit (Score: {best_score:.4f})")
            return best_result
            
        return None

    def set(self, query: str, result: Dict[str, Any]):
        # A. Set Exact Cache
        self.exact_cache[query] = result
        
        # B. Set Semantic Cache
        # Evict if full (Random/FIFO - using simple slice for now)
        if len(self.semantic_cache) >= self.max_semantic_size:
            self.semantic_cache.pop(0)
            
        query_embedding = vector_store.embedding_fn([query])[0]
        self.semantic_cache.append({
            "embedding": query_embedding,
            "result": result
        })

    def _cosine_similarity(self, vec_a, vec_b):
        # Convert to numpy
        a = np.array(vec_a)
        b = np.array(vec_b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(a, b) / (norm_a * norm_b)

# Singleton
cache_manager = CacheManager()
