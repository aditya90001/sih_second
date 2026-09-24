from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.rag.engine import rag_engine

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    well_id: str
    radius_km: Optional[float] = 10.0

class EvidenceSchema(BaseModel):
    well_id: str
    depth: float
    event: str
    source_document: str
    page: int

class ChatResponse(BaseModel):
    answer: str
    evidence: List[EvidenceSchema]

@router.post("", response_model=ChatResponse)
def query_drilling_knowledge(req: ChatRequest, db: Session = Depends(get_db)):
    results = rag_engine.hybrid_search(query=req.question, top_k=3)
    
    if not results:
        return ChatResponse(
            answer="Insufficient historical evidence was found in the indexed data.",
            evidence=[]
        )

    evidence_list = []
    answer_lines = ["DIRECT ANSWER BASED ON HISTORICAL EVIDENCE:"]

    for res in results:
        meta = res.get("metadata", {})
        required_fields = ("well_id", "depth", "event_type", "file_name", "page_number")
        if not all(meta.get(field) is not None for field in required_fields):
            continue

        evidence_list.append(EvidenceSchema(
            well_id=str(meta["well_id"]),
            depth=float(meta["depth"]),
            event=str(meta["event_type"]),
            source_document=str(meta["file_name"]),
            page=int(meta["page_number"])
        ))
        formation = meta.get("formation")
        location = f" in {formation}" if formation else ""
        answer_lines.append(f"- At depth {meta['depth']}m{location}: {res['text']}")

    if not evidence_list:
        return ChatResponse(
            answer="Insufficient historical evidence was found in the indexed data.",
            evidence=[]
        )

    return ChatResponse(
        answer="\n".join(answer_lines),
        evidence=evidence_list
    )
