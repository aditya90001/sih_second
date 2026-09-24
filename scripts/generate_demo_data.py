import os
import sys
import random
from datetime import datetime, timedelta

# Append app path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.core.database import SessionLocal, Base, engine
from app.models.domain import Well, Formation, DrillingEvent, DrillingParameter, User
from app.models.enums import DataSourceType, WellType, WellStatus, EventType, EventSeverity, UserRole

def seed_demo_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data
    db.query(DrillingParameter).delete()
    db.query(DrillingEvent).delete()
    db.query(Formation).delete()
    db.query(Well).delete()
    db.query(User).delete()
    db.commit()

    print("Generating synthetic drilling network...")

    # Center location: Upper Assam Basin (Oil India active area)
    BASE_LAT = 27.3500
    BASE_LON = 95.3200

    # Formations template for Upper Assam
    FORMATIONS_TEMPLATE = [
        ("Alluvium", 0.0, 500.0, "Sand/Clay", "Normal"),
        ("Namsang Formation", 500.0, 1200.0, "Sandstone/Siltstone", "Normal"),
        ("Girujan Clay", 1200.0, 2200.0, "Mottled Clay/Shale", "Slightly Overpressured"),
        ("Tipam Sandstone", 2200.0, 3100.0, "Coarse Sandstone", "High Permeability / Loss Prone"),
        ("Barail Group", 3100.0, 3800.0, "Coal-Shale-Sandstone", "Overpressured / Gas Prone"),
        ("Kopili Formation", 3800.0, 4200.0, "Splintery Shale", "High Pressure / Instability")
    ]

    # Create 1 Active Well
    active_well = Well(
        well_id="ACTIVE-001",
        well_name="OIL-Makum-104",
        latitude=BASE_LAT,
        longitude=BASE_LON,
        field="Makum",
        block="AA-ONHP-2017/3",
        operator="Oil India Limited",
        spud_date=datetime.utcnow() - timedelta(days=20),
        total_depth=4000.0,
        current_depth=2760.0,
        well_type=WellType.ACTIVE,
        status=WellStatus.DRILLING,
        data_source_type=DataSourceType.SYNTHETIC
    )
    db.add(active_well)

    # Create 35 Historical Wells scattered within 15 km
    wells_list = [active_well]
    for i in range(1, 36):
        lat_offset = random.uniform(-0.12, 0.12)
        lon_offset = random.uniform(-0.12, 0.12)
        well = Well(
            well_id=f"OIL-{100+i}",
            well_name=f"OIL-Historical-{100+i}",
            latitude=BASE_LAT + lat_offset,
            longitude=BASE_LON + lon_offset,
            field=random.choice(["Makum", "Hapjan", "Jorajan", "Moran", "Digboi"]),
            block="AA-ONHP-2017/3",
            operator="Oil India Limited",
            spud_date=datetime.utcnow() - timedelta(days=365 * random.randint(2, 10)),
            completion_date=datetime.utcnow() - timedelta(days=365 * random.randint(1, 2)),
            total_depth=random.uniform(3200.0, 4200.0),
            current_depth=0.0,
            well_type=WellType.HISTORICAL,
            status=WellStatus.COMPLETED,
            data_source_type=DataSourceType.SYNTHETIC
        )
        db.add(well)
        wells_list.append(well)

    db.commit()

    # Populate Formations and Events for all wells
    for well in wells_list:
        for f_name, top, bot, lith, press in FORMATIONS_TEMPLATE:
            if top <= well.total_depth:
                f_entry = Formation(
                    well_id=well.id,
                    formation_name=f_name,
                    top_depth=top,
                    bottom_depth=min(bot, well.total_depth),
                    lithology=lith,
                    pressure_regime=press,
                    risk_notes=f"Historical observations recorded in {f_name}",
                    data_source_type=DataSourceType.SYNTHETIC
                )
                db.add(f_entry)

        # Generate realistic, depth-correlated risk events for historical wells
        if well.well_type == WellType.HISTORICAL:
            num_events = random.randint(3, 8)
            for _ in range(num_events):
                # High loss frequency in Tipam Sandstone (2200-3100m)
                if random.random() < 0.5:
                    depth = random.uniform(2200.0, 3100.0)
                    e_type = EventType.MUD_LOSS
                    desc = f"Severe mud loss observed at {depth:.1f}m in Tipam Sandstone during circulation."
                    mit = "Pill pumped with 30 ppb LCM blend. Lost 45 bbls mud."
                    sev = EventSeverity.HIGH
                else:
                    depth = random.uniform(3100.0, well.total_depth)
                    e_type = random.choice([EventType.STUCK_PIPE, EventType.TORQUE_SPIKE, EventType.KICK])
                    desc = f"Observed {e_type.value} incident at {depth:.1f}m."
                    mit = "Worked pipe, adjusted mud parameters, resumed drilling."
                    sev = random.choice([EventSeverity.MEDIUM, EventSeverity.HIGH])

                event = DrillingEvent(
                    well_id=well.id,
                    depth=round(depth, 1),
                    formation="Tipam Sandstone" if depth < 3100 else "Barail Group",
                    event_type=e_type,
                    severity=sev,
                    description=desc,
                    cause="Geological structural weakness and differential pressure.",
                    mitigation=mit,
                    npt_hours=round(random.uniform(2.5, 18.0), 1),
                    event_date=well.spud_date + timedelta(days=random.randint(5, 30)),
                    data_source_type=DataSourceType.SYNTHETIC
                )
                db.add(event)

    db.flush()

    # Generate depth-indexed synthetic telemetry for the ML demo.
    for well in wells_list:
        well_events = db.query(DrillingEvent).filter(DrillingEvent.well_id == well.id).all()
        for depth in range(100, int(well.total_depth) + 1, 50):
            nearby_event = min(
                well_events,
                key=lambda event: abs(event.depth - depth),
                default=None,
            )
            event_nearby = nearby_event is not None and abs(nearby_event.depth - depth) <= 25
            event_type = nearby_event.event_type if event_nearby else None

            torque = random.uniform(10.0, 18.0)
            wob = random.uniform(8.0, 16.0)
            mud_weight = random.uniform(1.05, 1.25)
            standpipe_pressure = random.uniform(90.0, 150.0)

            if event_type == EventType.TORQUE_SPIKE:
                torque += random.uniform(12.0, 25.0)
                wob += random.uniform(3.0, 8.0)
            elif event_type == EventType.MUD_LOSS:
                mud_weight -= random.uniform(0.05, 0.12)
            elif event_type == EventType.KICK:
                standpipe_pressure += random.uniform(20.0, 50.0)

            db.add(DrillingParameter(
                well_id=well.id,
                timestamp=well.spud_date + timedelta(minutes=depth * 3),
                depth=float(depth),
                rop=random.uniform(4.0, 18.0),
                wob=round(wob, 2),
                rpm=random.uniform(70.0, 150.0),
                torque=round(torque, 2),
                hook_load=random.uniform(80.0, 140.0),
                standpipe_pressure=round(standpipe_pressure, 2),
                mud_weight=round(mud_weight, 3),
                flow_rate=random.uniform(800.0, 1200.0),
                pump_pressure=random.uniform(100.0, 180.0),
                ecd=round(mud_weight + random.uniform(0.02, 0.08), 3),
                temperature=random.uniform(70.0, 120.0),
                data_source_type=DataSourceType.SYNTHETIC,
            ))

    db.commit()
    print("Database seeding completed successfully.")
    db.close()

if __name__ == "__main__":
    seed_demo_data()