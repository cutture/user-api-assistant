
from rank_bm25 import BM25Okapi
from core.vector_store import store as vector_store
from typing import List, Dict, Any
import numpy as np
import re

class HybridRetriever:
    def __init__(self):
        self.bm25 = None
        self.doc_registry = {} # Map index -> (id, content, metadata)
        self.corpus = []
        
        # Initial Sync
        self.sync_index()

    def sync_index(self):
        """
        Fetches all docs from Vector Store and builds BM25 index.
        Should be called on startup and after uploads.
        """
        print("🔄 Syncing BM25 Index...")
        data = vector_store.get_all_documents()
        
        if not data or not data.get("documents"):
            print("⚠️ No documents found in Vector Store to sync.")
            self.bm25 = None
            return

        documents = data["documents"]
        ids = data["ids"]
        metadatas = data["metadatas"]
        
        self.corpus = documents
        self.doc_registry = {i: {"id": ids[i], "content": doc, "metadata": metadatas[i] if metadatas else {}} 
                             for i, doc in enumerate(documents)}
        
        # Tokenize
        tokenized_corpus = [self._tokenize(doc) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(f"✅ BM25 Index Built with {len(documents)} documents.")

    def _tokenize(self, text: str) -> List[str]:
        # Simple whitespace + alphanumeric tokenizer
        # "Hello, world!" -> ["hello", "world"]
        return re.findall(r'\w+', text.lower())

    def search(self, query: str, n_results: int = 3, fusion_weight: float = 0.5, filters: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Performs Hybrid Search using Reciprocal Rank Fusion (RRF).
        Enriched with Caching and Query Expansion.
        """
        from core.cache import cache_manager
        from core.expansion import expander
        from core.filtering import filter_manager
        
        # 0. Parse Filters from Query
        clean_query, parsed_filters = filter_manager.parse_query(query)
        
        # Merge Explicit Filters (CLI/API) with Parsed Filters
        combined_filters = {}
        if parsed_filters:
            combined_filters.update(parsed_filters)
        if filters:
            combined_filters.update(filters)
            
        if combined_filters:
            print(f"🔎 Filters: {combined_filters} | Clean Query: '{clean_query}'")
            # Update query to clean version for search
            query = clean_query
            
            # Use combined filters
            filters = combined_filters
        else:
            filters = None
        
        # 1. Check Cache
        # Cache key should include filters to avoid incorrect hits
        cache_key = f"{query}::{sorted(filters.items()) if filters else ''}"
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        # 2. Expand Query
        expanded_queries = expander.expand(query)
        
        all_vector_results = []
        all_bm25_hits = []
        
        # 3. Search for ALL variations
        
        for q in expanded_queries:
             # A. Semantic Search (Vector)
            # Pass filters to vector store
            v_res = vector_store.query(q, n_results=n_results * 2, where=filters)
            if v_res and v_res['ids']:
                all_vector_results.extend(zip(v_res['ids'][0], range(len(v_res['ids'][0]))))

            # B. Keyword Search (BM25)
            if self.bm25:
                tokenized_q = self._tokenize(q)
                scores = self.bm25.get_scores(tokenized_q)
                top_n_indices = np.argsort(scores)[::-1][:n_results * 4] # Fetch more to allow for filtering
                
                for idx in top_n_indices:
                    # POST-FILTERING for BM25
                    if filters:
                        # Check metadata
                        doc_meta = self.doc_registry[idx]["metadata"]
                        match = True
                        for k, v in filters.items():
                            if str(doc_meta.get(k, "")).lower() != str(v).lower():
                                match = False
                                break
                        if not match:
                            continue

                    if scores[idx] > 0:
                        all_bm25_hits.append({
                            "id": self.doc_registry[idx]["id"],
                            "score": scores[idx]
                        })

        # 4. Fusion (RRF)
        # We need to deduplicate based on ID and sum inverse ranks
        
        # 4. Fusion (RRF)
        # We need to deduplicate based on ID and sum inverse ranks
        
        fused_scores = {}
        k = 60
        
        # Process Vector Hits
        for doc_id, rank in all_vector_results:
             if doc_id not in fused_scores: fused_scores[doc_id] = 0
             fused_scores[doc_id] += 1 / (k + rank + 1)
             
        # Process BM25 Hits
        all_bm25_hits.sort(key=lambda x: x['score'], reverse=True)
        for rank, hit in enumerate(all_bm25_hits):
            doc_id = hit["id"]
            if doc_id not in fused_scores: fused_scores[doc_id] = 0
            fused_scores[doc_id] += 1 / (k + rank + 1)
            
        # Get Candidates for MMR
        # We need embedding for MMR. Lookup from registry.
        candidate_ids = sorted(fused_scores, key=fused_scores.get, reverse=True)[:n_results * 3] # Fetch 3x candidates
        
        candidates_for_mmr = []
        from core.diversification import ranker as mmr_ranker

        for cid in candidate_ids:
            # Find metadata/content
            found = None
            for item in self.doc_registry.values():
                if item["id"] == cid:
                    found = item
                    break
            
            if found:
                # Need embedding. If not in registry, we might need to fetch or cache it.
                # For now, let's assume we can get it or compute it?
                # Re-computing embedding on fly is slow.
                # Ideally registry has embedding.
                # In sync_index, we fetched 'documents' and 'metadatas'. Chroma 'get' implies we can get embeddings too.
                # Let's fix sync_index to include embeddings if feasible, OR re-embed here (slow).
                
                # OPTIMIZATION: Check semantic cache for embedding or use vector_store result?
                # Chroma query result includes embeddings if asked.
                # Let's assume we don't have it easily. We will skip MMR if no embedding.
                pass 
                
                # If we updated sync_index to fetch embeddings, that would be best.
                # But loading ALL embeddings into memory might be heavy.
                # HybridRetriever is in-memory heavy anyway with BM25.
                # Let's update candidates construction to be simple for now, 
                # passing empty embedding to fail gracefully or improvement later.
                
                # For THIS Step, since we haven't updated sync_index to store embeddings, 
                # we will fetch embedding for these top candidates specifically.
                pass

        # RE-FETCH embeddings for top N candidates (efficient enough for <20 items)
        if candidate_ids:
            try:
                emb_data = vector_store._get_collection().get(ids=candidate_ids, include=["embeddings"])
                # Map ID -> Embedding
                id_to_emb = {id: emb for id, emb in zip(emb_data['ids'], emb_data['embeddings'])}
                
                for cid in candidate_ids:
                    if cid in id_to_emb:
                        # Find content in registry
                        content = ""
                        for item in self.doc_registry.values():
                            if item["id"] == cid:
                                content = item["content"]
                                break
                        
                        candidates_for_mmr.append({
                            "id": cid,
                            "embedding": id_to_emb[cid],
                            "content": content
                        })
            except Exception as e:
                print(f"⚠️ Failed to fetch embeddings for MMR: {e}")

        # 5. Apply MMR Re-ranking
        # Need query embedding
        query_embedding = vector_store.embedding_fn([query])[0]
        
        final_docs_dicts = mmr_ranker.rerank(query_embedding, candidates_for_mmr, top_n=n_results)
        
        final_docs = [d["content"] for d in final_docs_dicts]
        sorted_ids = [d["id"] for d in final_docs_dicts]
            
        result = {"documents": [final_docs], "ids": [sorted_ids]}
        
        # 6. Set Cache
        cache_manager.set(cache_key, result)
        
        return result


# Singleton
hybrid_retriever = HybridRetriever()
