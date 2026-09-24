from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.rag.engine import rag_engine
from app.rag.query_parser import QueryParser

router = APIRouter()
query_parser = QueryParser()

class SearchRequest(BaseModel):
    query: str
    well_id: Optional[str] = None
    radius_km: Optional[float] = 10.0

class SearchResultItem(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    parsed_filters: Dict[str, Any]
    results: List[SearchResultItem]

@router.post("", response_model=SearchResponse)
def structured_search(req: SearchRequest):
    # 1. Parse natural language intent into structured parameters
    parsed_intent = query_parser.parse(req.query)
    
    # 2. Build filters
    filters = {}
    if parsed_intent.get("event_type"):
        filters["event_type"] = parsed_intent["event_type"]

    # 3. Search RAG
    raw_results = rag_engine.hybrid_search(
        query=req.query,
        filters=filters if filters else None,
        top_k=5
    )

    formatted = [
        SearchResultItem(text=r["text"], score=r["score"], metadata=r["metadata"])
        for r in raw_results
    ]

    return SearchResponse(
        query=req.query,
        parsed_filters=parsed_intent,
        results=formatted
    )