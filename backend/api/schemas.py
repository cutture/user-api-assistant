
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query string")
    filters: Optional[Dict[str, str]] = Field(None, description="Metadata filters (key:value)")
    limit: int = Field(5, ge=1, le=20, description="Max number of results to return")
    use_mmr: bool = Field(True, description="Enable Maximum Marginal Relevance diversification")
    mmr_lambda: float = Field(0.5, ge=0.0, le=1.0, description="Diversity vs Relevance trade-off (0.0=Diverse, 1.0=Relevant)")

class SearchResultItem(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None # RRF doesn't provide meaningful absolute scores easily, but we can try

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    count: int
