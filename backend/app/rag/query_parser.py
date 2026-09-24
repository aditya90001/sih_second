import re
from typing import Dict, Any

class QueryParser:
    def __init__(self):
        self.depth_pattern = re.compile(r"(\d{3,5})\s*(?:m|meters)", re.IGNORECASE)

    def parse(self, query: str) -> Dict[str, Any]:
        result = {}
        depth_match = self.depth_pattern.search(query)
        if depth_match:
            result["depth"] = float(depth_match.group(1))

        q_lower = query.lower()
        if "mud loss" in q_lower or "loss" in q_lower:
            result["event_type"] = "MUD_LOSS"
        elif "stuck pipe" in q_lower or "stuck" in q_lower:
            result["event_type"] = "STUCK_PIPE"
        elif "kick" in q_lower:
            result["event_type"] = "KICK"

        return result