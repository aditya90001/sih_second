import os
import joblib
import pandas as pd
from typing import Dict, Any, List

class RiskPredictor:
    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = model_dir
        self.models = {}
        self.features = ['depth', 'rop', 'wob', 'rpm', 'torque', 'hook_load', 'standpipe_pressure', 'mud_weight', 'flow_rate', 'ecd']
        self._load_models()

    def _load_models(self):
        targets = ['is_mud_loss', 'is_stuck_pipe', 'is_kick', 'is_torque_spike']
        for t in targets:
            path = os.path.join(self.model_dir, f"{t}_model.pkl")
            if os.path.exists(path):
                self.models[t] = joblib.load(path)

    def predict_risks(self, parameter_dict: Dict[str, float]) -> Dict[str, Any]:
        """
        Takes real-time telemetry dictionary and returns explainable model-estimated probabilities.
        """
        df_input = pd.DataFrame([parameter_dict])
        
        # Ensure all feature columns exist with defaults
        for f in self.features:
            if f not in df_input.columns:
                df_input[f] = 0.0

        X = df_input[self.features]

        predictions = {}
        top_features = {}

        for target_name, model in self.models.items():
            prob = model.predict_proba(X)[0][1] if hasattr(model, "predict_proba") else 0.0
            risk_label = target_name.replace("is_", "").upper()
            
            predictions[risk_label] = round(float(prob), 3)

            # Feature Importance
            if hasattr(model, "feature_importances_"):
                importances = dict(zip(self.features, model.feature_importances_))
                sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:3]
                top_features[risk_label] = [k for k, v in sorted_imp]

        return {
            "disclaimer": "Model-estimated probability based on historical training data. Decision support only.",
            "model_version": "v1.0.0-RandomForest",
            "probabilities": predictions,
            "important_features": top_features
        }