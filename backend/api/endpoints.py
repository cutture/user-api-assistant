
from fastapi import APIRouter, HTTPException, Depends
from api.schemas import SearchRequest, SearchResponse, SearchResultItem
from core.hybrid import hybrid_retriever
from core.exceptions import AppError

router = APIRouter(tags=["Advanced Search"])

@router.post("/v1/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Performs an advanced hybrid search with support for:
    - Semantic + Keyword Search (RRF Fusion)
    - Query Expansion
    - Metadata Filtering
    - MMR Diversification
    - Semantic Caching
    """
    try:
        # 1. Prepare Filters
        # Merging request filters with any parsed from query? 
        # For this strict API, we trust explicit 'filters' dict more, 
        # but hybrid_retriever.search might also parse string.
        # Let's rely on hybrid_retriever's internal logic which now accepts check 'filters' arg.
        
        # NOTE: hybrid_retriever.search signature:
        # search(query: str, n_results: int = 3, fusion_weight: float = 0.5, filters: dict = None)
        # It does NOT properly expose MMR lambda yet?
        # Actually core.hybrid.py hardcoded lambda to 0.5 in previous implementation?
        # Let's check hybrid.py. It calls mmr_ranker.rerank(..., top_n=n_results)
        # It uses default logic.
        # TODO: We might need to update HybridRetriever to accept mmr_lambda if we want to expose it.
        # For now, we proceed with defaults.
        
        results = hybrid_retriever.search(
            query=request.query,
            n_results=request.limit,
            filters=request.filters
        )
        
        # Results format: {"documents": [[...]], "ids": [[...]]}
        # Wait, where is metadata?
        # HybridRetriever currently returns {"documents": [...], "ids": [...]}.
        # It relies on `doc_registry` index lookup.
        # We need to fetch metadata to return it.
        
        final_docs = results.get("documents", [[]])[0]
        final_ids = results.get("ids", [[]])[0]
        
        response_items = []
        for doc_content, doc_id in zip(final_docs, final_ids):
             # Find Metadata in Registry
             # Registry is typically {int_index: {id, content, metadata}}
             # Reverse lookup? Or we iterate.
             # Ideally HybridRetriever returns metadata.
             
             meta = {}
             # Inefficient Lookup
             for item in hybrid_retriever.doc_registry.values():
                 if item["id"] == doc_id:
                     meta = item.get("metadata", {})
                     break
            
             response_items.append(SearchResultItem(
                 id=doc_id,
                 content=doc_content,
                 metadata=meta,
                 score=None 
             ))
             
        return SearchResponse(
            query=request.query,
            results=response_items,
            count=len(response_items)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
