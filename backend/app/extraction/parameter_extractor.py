import re
from typing import Dict, Any, Optional

class ParameterExtractor:
    """Parses numeric telemetry logs from unstructured daily drilling reports (DDR)."""
    def __init__(self):
        self.rop_pattern = re.compile(r"ROP[:\s]+(\d+(?:\.\d+)?)\s*m/hr", re.IGNORECASE)
        self.wob_pattern = re.compile(r"WOB[:\s]+(\d+(?:\.\d+)?)\s*klbs", re.IGNORECASE)
        self.mw_pattern = re.compile(r"Mud\s*Weight[:\s]+(\d+(?:\.\d+)?)\s*sg", re.IGNORECASE)

    def extract_parameters(self, line: str) -> Dict[str, Optional[float]]:
        rop_m = self.rop_pattern.search(line)
        wob_m = self.wob_pattern.search(line)
        mw_m = self.mw_pattern.search(line)

        return {
            "rop": float(rop_m.group(1)) if rop_m else None,
            "wob": float(wob_m.group(1)) if wob_m else None,
            "mud_weight": float(mw_m.group(1)) if mw_m else None
        }