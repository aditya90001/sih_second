import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib

def train_risk_models(df: pd.DataFrame, model_output_dir: str = "data/models"):
    """
    Trains risk prediction models using strict Well-Level Splitting.
    Preventing data leakage between identical well parameter logs.
    """
    os.makedirs(model_output_dir, exist_ok=True)
    
    unique_wells = df['well_id'].unique()
    rng = np.random.default_rng(42)
    rng.shuffle(unique_wells)

    n_wells = len(unique_wells)
    train_end = int(n_wells * 0.70)
    val_end = int(n_wells * 0.85)

    train_wells = unique_wells[:train_end]
    val_wells = unique_wells[train_end:val_end]
    test_wells = unique_wells[val_end:]

    train_df = df[df['well_id'].isin(train_wells)]
    val_df = df[df['well_id'].isin(val_wells)]
    test_df = df[df['well_id'].isin(test_wells)]

    features = ['depth', 'rop', 'wob', 'rpm', 'torque', 'hook_load', 'standpipe_pressure', 'mud_weight', 'flow_rate', 'ecd']
    targets = ['is_mud_loss', 'is_stuck_pipe', 'is_kick', 'is_torque_spike']

    results = {}

    for target in targets:
        print(f"\nTraining Model for Target Risk: {target}")
        
        X_train, y_train = train_df[features], train_df[target]
        X_test, y_test = test_df[features], test_df[target]

        if y_train.nunique() < 2:
            print(f"Skipping {target}: training split contains one class only")
            continue
        if y_test.empty:
            print(f"Skipping {target}: test split is empty")
            continue

        model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        positive_class_index = list(model.classes_).index(1)
        y_prob = model.predict_proba(X_test)[:, positive_class_index]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else 0.5

        print(f"Metrics for {target}:")
        print(f"  Accuracy : {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall   : {rec:.4f}")
        print(f"  F1-Score : {f1:.4f}")
        print(f"  ROC-AUC  : {auc:.4f}")

        # Save model
        model_path = os.path.join(model_output_dir, f"{target}_model.pkl")
        joblib.dump(model, model_path)
        
        results[target] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(auc, 4)
        }

    return results