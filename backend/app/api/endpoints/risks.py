from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any
from app.ml.predictor import RiskPredictor

router = APIRouter()
predictor = RiskPredictor()

class RiskPredictionRequest(BaseModel):
    well_id: str
    depth: float
    rop: float
    wob: float
    rpm: float
    torque: float
    hook_load: float
    standpipe_pressure: float
    mud_weight: float
    flow_rate: float
    ecd: float

class RiskPredictionResponse(BaseModel):
    disclaimer: str
    model_version: str
    probabilities: Dict[str, float]
    important_features: Dict[str, Any]

@router.post("/predict", response_model=RiskPredictionResponse)
def predict_drilling_risk(req: RiskPredictionRequest):
    param_dict = req.model_dump()
    result = predictor.predict_risks(param_dict)
    return result