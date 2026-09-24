from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.models.enums import EventType, EventSeverity

class FormationSchema(BaseModel):
    id: int
    well_id: int
    formation_name: str
    top_depth: float
    bottom_depth: float
    lithology: str
    pressure_regime: str
    risk_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class RiskZoneSchema(BaseModel):
    top_depth: float
    bottom_depth: float
    formation: str
    event_type: EventType
    occurrence_count: int
    well_count: int
    wells_affected: List[str]
    severity_distribution: dict

class DrillingParameterSchema(BaseModel):
    id: int
    well_id: int
    depth: float
    rop: float
    wob: float
    rpm: float
    torque: float
    hook_load: float
    standpipe_pressure: float
    mud_weight: float
    flow_rate: float
    pump_pressure: float
    ecd: float
    temperature: float

    model_config = ConfigDict(from_attributes=True)