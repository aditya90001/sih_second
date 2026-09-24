from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.domain import Alert, Well
from app.schemas.alert import AlertSchema, AlertEvaluationRequest
from app.services.alert_service import AlertEngine

router = APIRouter()
alert_engine = AlertEngine()

@router.get("", response_model=List[AlertSchema])
def get_active_alerts(
    well_id: Optional[str] = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if well_id:
        well = db.query(Well).filter(Well.well_id == well_id).first()
        if well:
            query = query.filter(Alert.well_id == well.id)
    return query.order_by(Alert.created_at.desc()).limit(limit).all()

@router.post("/evaluate", response_model=List[AlertSchema])
def evaluate_well_alerts(req: AlertEvaluationRequest, db: Session = Depends(get_db)):
    alerts = alert_engine.evaluate_depth_alerts(
        db=db,
        well_id=req.well_id,
        current_depth=req.current_depth,
        radius_km=req.radius_km
    )
    return alerts