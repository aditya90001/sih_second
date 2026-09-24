import re
from typing import List, Dict, Any

class FormationExtractor:
    def __init__(self):
        self.formation_pattern = re.compile(
            r"(Formation\s+[A-Z0-9_-]+|Tipam\s+Sandstone|Barail\s+Group|Girujan\s+Clay|Kopili\s+Shale|Namsang\s+Formation)",
            re.IGNORECASE
        )
        self.depth_range_pattern = re.compile(
            r"from\s+(\d{3,5}(?:\.\d+)?)\s*(?:m|meters)?\s+to\s+(\d{3,5}(?:\.\d+)?)\s*(?:m|meters)?",
            re.IGNORECASE
        )

    def extract_formations_from_text(self, text: str) -> List[Dict[str, Any]]:
        results = []
        lines = text.split("\n")
        for line in lines:
            f_match = self.formation_pattern.search(line)
            d_match = self.depth_range_pattern.search(line)
            if f_match and d_match:
                results.append({
                    "formation_name": f_match.group(1),
                    "top_depth": float(d_match.group(1)),
                    "bottom_depth": float(d_match.group(2)),
                    "confidence": 0.90
                })
        return results