import re
from typing import Dict, Any, Optional
from app.models.enums import EventType, EventSeverity

class EventExtractor:
    def __init__(self):
        # Patterns for drilling metrics and events
        self.depth_pattern = re.compile(r"(\d{3,5}(?:\.\d+)?)\s*(?:m|meters|ft)", re.IGNORECASE)
        self.formation_pattern = re.compile(r"(Formation\s+[A-Z0-9_-]+|Tipam\s+Sandstone|Barail\s+Group|Girujan\s+Clay|Kopili\s+Shale)", re.IGNORECASE)
        
    def extract_structured_event(self, text: str) -> Dict[str, Any]:
        """
        Regex + Deterministic Rules Extractor with zero hallucination.
        """
        depth_match = self.depth_pattern.search(text)
        depth = float(depth_match.group(1)) if depth_match else None

        formation_match = self.formation_pattern.search(text)
        formation = formation_match.group(1) if formation_match else None

        # Event type identification
        text_lower = text.lower()
        event_type = None
        if "mud loss" in text_lower or "lost circulation" in text_lower:
            event_type = EventType.MUD_LOSS
        elif "stuck pipe" in text_lower or "stuck" in text_lower:
            event_type = EventType.STUCK_PIPE
        elif "kick" in text_lower or "well control" in text_lower:
            event_type = EventType.KICK
        elif "torque" in text_lower:
            event_type = EventType.TORQUE_SPIKE

        # Severity identification
        severity = EventSeverity.MEDIUM
        if "severe" in text_lower or "critical" in text_lower or "total loss" in text_lower:
            severity = EventSeverity.HIGH
        elif "minor" in text_lower or "slight" in text_lower:
            severity = EventSeverity.LOW

        # Mitigation extraction
        mitigation = None
        if "lcm" in text_lower or "pill" in text_lower:
            mitigation_match = re.search(r"((?:LCM|pill)[^.]*)", text, re.IGNORECASE)
            mitigation = mitigation_match.group(1).strip() if mitigation_match else "LCM treatment performed"

        return {
            "depth": depth,
            "formation": formation,
            "event_type": event_type.value if event_type else None,
            "severity": severity.value,
            "mitigation": mitigation,
            "confidence": 0.95 if (depth and event_type) else 0.50
        }