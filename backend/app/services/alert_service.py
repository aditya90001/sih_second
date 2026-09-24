import math
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.domain import Well, DrillingEvent, Alert
from app.models.enums import EventType, EventSeverity
from app.core.geospatial import haversine_distance

class AlertEngine:
    def evaluate_depth_alerts(
        self,
        db: Session,
        well_id: str,
        current_depth: float,
        radius_km: float = 10.0,
        lookahead_m: float = 100.0
    ) -> List[Alert]:
        """
        Evaluates whether active well is approaching historical risk zones within lookahead window.
        """
        active_well = db.query(Well).filter(Well.well_id == well_id).first()
        if not active_well:
            return []

        # 1. Find nearby wells
        all_wells = db.query(Well).filter(Well.id != active_well.id).all()
        nearby_well_ids = []
        well_dist_map = {}

        for w in all_wells:
            dist = haversine_distance(active_well.latitude, active_well.longitude, w.latitude, w.longitude)
            if dist <= radius_km:
                nearby_well_ids.append(w.id)
                well_dist_map[w.id] = (w.well_name, dist)

        if not nearby_well_ids:
            return []

        # 2. Check historical events in upcoming depth window (current_depth to current_depth + lookahead_m)
        target_top = current_depth
        target_bottom = current_depth + lookahead_m

        events = db.query(DrillingEvent).filter(
            DrillingEvent.well_id.in_(nearby_well_ids),
            DrillingEvent.depth >= target_top - 50.0,
            DrillingEvent.depth <= target_bottom + 50.0
        ).all()

        # Group by event type
        event_groups = {}
        for ev in events:
            ev_type = ev.event_type.value
            if ev_type not in event_groups:
                event_groups[ev_type] = []
            event_groups[ev_type].append(ev)

        generated_alerts = []

        # 3. Rule: Generate alert if >= 2 historical occurrences or >= 2 affected wells (avoid single isolated event noise)
        for ev_type, ev_list in event_groups.items():
            affected_wells = set([ev.well_id for ev in ev_list])
            
            if len(ev_list) >= 2 or len(affected_wells) >= 2:
                evidence_data = []
                for ev in ev_list:
                    w_name, dist = well_dist_map[ev.well_id]
                    evidence_data.append({
                        "well_name": w_name,
                        "depth": ev.depth,
                        "formation": ev.formation,
                        "mitigation": ev.mitigation,
                        "distance_km": dist
                    })

                msg = f"Current well is approaching a historical {ev_type} interval ({target_top:.0f}m - {target_bottom:.0f}m) observed in {len(affected_wells)} nearby wells ({len(ev_list)} total occurrences)."

                alert_obj = Alert(
                    well_id=active_well.id,
                    depth=current_depth,
                    alert_type=EventType(ev_type),
                    severity=EventSeverity.HIGH if len(ev_list) >= 4 else EventSeverity.MEDIUM,
                    message=msg,
                    historical_evidence_json={
                        "summary_count": len(ev_list),
                        "affected_wells_count": len(affected_wells),
                        "evidence": evidence_data
                    },
                    status="ACTIVE"
                )
                db.add(alert_obj)
                generated_alerts.append(alert_obj)

        db.commit()
        return generated_alerts