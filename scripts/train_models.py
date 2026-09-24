import os
import sys
import pandas as pd
import numpy as np

# Append backend directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.core.database import SessionLocal
from app.models.domain import Well, DrillingParameter, DrillingEvent
from app.models.enums import EventType
from app.ml.train import train_risk_models

def extract_training_dataset():
    """
    Fetches parameters and events from SQLite database and formats 
    a supervised feature matrix for ML training with target risk flags.
    """
    db = SessionLocal()
    print("Fetching drilling telemetry logs from database...")
    
    # Query all parameter records
    params = db.query(DrillingParameter).all()
    if not params:
        print("No parameter data found in database. Please run generate_demo_data.py first.")
        db.close()
        return None

    param_list = []
    for p in params:
        well = db.query(Well).filter(Well.id == p.well_id).first()
        param_list.append({
            "well_id": well.well_id if well else f"WELL-{p.well_id}",
            "depth": p.depth,
            "rop": p.rop,
            "wob": p.wob,
            "rpm": p.rpm,
            "torque": p.torque,
            "hook_load": p.hook_load,
            "standpipe_pressure": p.standpipe_pressure,
            "mud_weight": p.mud_weight,
            "flow_rate": p.flow_rate,
            "ecd": p.ecd
        })

    df = pd.DataFrame(param_list)

    # Query all historical drilling events
    events = db.query(DrillingEvent).all()
    
    # Initialize target binary labels
    df["is_mud_loss"] = 0
    df["is_stuck_pipe"] = 0
    df["is_kick"] = 0
    df["is_torque_spike"] = 0

    print(f"Correlating {len(events)} historical risk events across {len(df)} depth telemetry records...")

    # Label depth windows (+/- 15 meters around recorded event depth)
    for ev in events:
        well = db.query(Well).filter(Well.id == ev.well_id).first()
        if not well:
            continue
        
        well_str_id = well.well_id
        ev_depth = ev.depth
        ev_type = ev.event_type.value if hasattr(ev.event_type, 'value') else str(ev.event_type)

        mask = (df["well_id"] == well_str_id) & (df["depth"].between(ev_depth - 15.0, ev_depth + 15.0))

        if ev_type == EventType.MUD_LOSS.value:
            df.loc[mask, "is_mud_loss"] = 1
        elif ev_type == EventType.STUCK_PIPE.value:
            df.loc[mask, "is_stuck_pipe"] = 1
        elif ev_type == EventType.KICK.value:
            df.loc[mask, "is_kick"] = 1
        elif ev_type == EventType.TORQUE_SPIKE.value:
            df.loc[mask, "is_torque_spike"] = 1

    db.close()
    return df

def main():
    df = extract_training_dataset()
    if df is None or df.empty:
        print("Training aborted due to empty dataset.")
        return

    print(f"Dataset successfully compiled: {len(df)} records across {df['well_id'].nunique()} unique wells.")
    print("Target class distribution:")
    print(f"  Mud Loss Events   : {df['is_mud_loss'].sum()} depth windows")
    print(f"  Stuck Pipe Events : {df['is_stuck_pipe'].sum()} depth windows")
    print(f"  Kick Events       : {df['is_kick'].sum()} depth windows")
    print(f"  Torque Spike Events: {df['is_torque_spike'].sum()} depth windows")

    print("\nExecuting Machine Learning Pipeline with Strict Well-Level Split...")
    metrics = train_risk_models(df, model_output_dir="data/models")
    
    print("\n==================================================")
    print("ML RISK MODEL TRAINING COMPLETED SUCCESSFULLY")
    print("Models stored in: data/models/")
    print("==================================================")

if __name__ == "__main__":
    main()