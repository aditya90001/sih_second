from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.domain import Well, DrillingEvent
from app.schemas.well import WellSchema, NearbyWellSchema, DrillingEventSchema
from app.core.geospatial import haversine_distance
import math

router = APIRouter()
from app.models.domain import Formation, DrillingParameter, DrillingEvent
from app.schemas.risk import FormationSchema, DrillingParameterSchema, RiskZoneSchema

@router.get("/{well_id}/formations", response_model=List[FormationSchema])
def get_well_formations(well_id: str, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.well_id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return db.query(Formation).filter(Formation.well_id == well.id).order_by(Formation.top_depth.asc()).all()

@router.get("/{well_id}/parameters", response_model=List[DrillingParameterSchema])
def get_well_parameters(well_id: str, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.well_id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return db.query(DrillingParameter).filter(DrillingParameter.well_id == well.id).order_by(DrillingParameter.depth.asc()).all()

@router.get("/{well_id}/risk-zones", response_model=List[RiskZoneSchema])
def get_nearby_risk_zones(
    well_id: str,
    radius_km: float = Query(10.0, description="Radius in KM"),
    db: Session = Depends(get_db)
):
    target_well = db.query(Well).filter(Well.well_id == well_id).first()
    if not target_well:
        raise HTTPException(status_code=404, detail="Target well not found")

    nearby = get_nearby_wells_by_coords(
        latitude=target_well.latitude,
        longitude=target_well.longitude,
        radius_km=radius_km,
        db=db
    )
    nearby_well_ids = [w.id for w in nearby if w.well_id != well_id]

    events = db.query(DrillingEvent).filter(DrillingEvent.well_id.in_(nearby_well_ids)).all()

    # Aggregate into 100-meter depth intervals
    zones_dict = {}
    for ev in events:
        interval_start = math.floor(ev.depth / 100.0) * 100.0
        interval_end = interval_start + 100.0
        key = (interval_start, interval_end, ev.event_type.value)

        if key not in zones_dict:
            zones_dict[key] = {
                "top_depth": interval_start,
                "bottom_depth": interval_end,
                "formation": ev.formation,
                "event_type": ev.event_type,
                "occurrences": 0,
                "wells": set(),
                "severities": {}
            }

        zones_dict[key]["occurrences"] += 1
        zones_dict[key]["wells"].add(ev.well_id)
        sev_str = ev.severity.value
        zones_dict[key]["severities"][sev_str] = zones_dict[key]["severities"].get(sev_str, 0) + 1

    risk_zones = []
    for key, data in zones_dict.items():
        # Exclude isolated single occurrences (historical risk zone rule)
        if data["occurrences"] >= 2 or len(data["wells"]) >= 2:
            well_names = [w.well_name for w in db.query(Well).filter(Well.id.in_(data["wells"])).all()]
            risk_zones.append(RiskZoneSchema(
                top_depth=data["top_depth"],
                bottom_depth=data["bottom_depth"],
                formation=data["formation"],
                event_type=data["event_type"],
                occurrence_count=data["occurrences"],
                well_count=len(data["wells"]),
                wells_affected=well_names,
                severity_distribution=data["severities"]
            ))

    risk_zones.sort(key=lambda x: x.top_depth)
    return risk_zones

@router.get("", response_model=List[WellSchema])
def get_wells(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Well).offset(skip).limit(limit).all()

@router.get("/nearby", response_model=List[NearbyWellSchema])
def get_nearby_wells_by_coords(
    latitude: float = Query(..., description="Latitude of target location"),
    longitude: float = Query(..., description="Longitude of target location"),
    radius_km: float = Query(10.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    all_wells = db.query(Well).all()
    results = []

    for well in all_wells:
        dist = haversine_distance(latitude, longitude, well.latitude, well.longitude)
        if dist <= radius_km:
            event_count = db.query(DrillingEvent).filter(DrillingEvent.well_id == well.id).count()
            
            # Simple risk summary calculation
            events = db.query(DrillingEvent).filter(DrillingEvent.well_id == well.id).all()
            risk_summary = {}
            for ev in events:
                risk_summary[ev.event_type.value] = risk_summary.get(ev.event_type.value, 0) + 1

            well_data = NearbyWellSchema(
                **WellSchema.model_validate(well).model_dump(),
                distance_km=dist,
                event_count=event_count,
                risk_summary=risk_summary
            )
            results.append(well_data)

    results.sort(key=lambda x: x.distance_km)
    return results

@router.get("/{well_id}", response_model=WellSchema)
def get_well(well_id: str, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.well_id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return well

@router.get("/{well_id}/nearby", response_model=List[NearbyWellSchema])
def get_nearby_wells_by_id(
    well_id: str,
    radius_km: float = Query(10.0, description="Radius in KM"),
    db: Session = Depends(get_db)
):
    target_well = db.query(Well).filter(Well.well_id == well_id).first()
    if not target_well:
        raise HTTPException(status_code=404, detail="Target well not found")

    return get_nearby_wells_by_coords(
        latitude=target_well.latitude,
        longitude=target_well.longitude,
        radius_km=radius_km,
        db=db
    )

@router.get("/{well_id}/events", response_model=List[DrillingEventSchema])
def get_well_events(well_id: str, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.well_id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return db.query(DrillingEvent).filter(DrillingEvent.well_id == well.id).all()