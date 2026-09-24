from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.enums import EventType, EventSeverity

class HistoricalEvidenceSchema(BaseModel):
    well_id: str
    well_name: str
    depth: float
    event_type: EventType
    mitigation: Optional[str] = None
    distance_km: float

class AlertSchema(BaseModel):
    id: int
    well_id: int
    depth: float
    alert_type: EventType
    severity: EventSeverity
    message: str
    historical_evidence_json: Dict[str, Any]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertEvaluationRequest(BaseModel):
    well_id: str
    current_depth: float
    radius_km: Optional[float] = 10.0