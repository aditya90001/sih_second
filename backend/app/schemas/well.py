from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.enums import DataSourceType, WellType, WellStatus, EventType, EventSeverity

class FormationSchema(BaseModel):
    id: int
    well_id: int
    formation_name: str
    top_depth: float
    bottom_depth: float
    lithology: str
    pressure_regime: str
    risk_notes: Optional[str] = None
    data_source_type: DataSourceType
    
    model_config = ConfigDict(from_attributes=True)

class DrillingEventSchema(BaseModel):
    id: int
    well_id: int
    depth: float
    formation: str
    event_type: EventType
    severity: EventSeverity
    description: str
    cause: Optional[str] = None
    mitigation: Optional[str] = None
    npt_hours: float
    event_date: Optional[datetime] = None
    source_document_id: Optional[int] = None
    page_number: Optional[int] = None
    data_source_type: DataSourceType
    
    model_config = ConfigDict(from_attributes=True)

class WellSchema(BaseModel):
    id: int
    well_id: str
    well_name: str
    latitude: float
    longitude: float
    field: str
    block: str
    operator: str
    spud_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    total_depth: float
    current_depth: float
    well_type: WellType
    status: WellStatus
    data_source_type: DataSourceType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NearbyWellSchema(WellSchema):
    distance_km: float
    event_count: int
    risk_summary: dict