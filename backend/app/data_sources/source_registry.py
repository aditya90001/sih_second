import os
import json
from datetime import datetime
from typing import List, Dict, Any

SOURCE_REGISTRY_FILE = "data/source_registry.json"

DEFAULT_SOURCES = [
    {
        "source_name": "Directorate General of Hydrocarbons (DGH) Open Data",
        "source_url": "https://dghindia.gov.in/index.php/page_single/index/48",
        "source_type": "web",
        "access_method": "requests",
        "last_checked": datetime.utcnow().isoformat(),
        "status": "UNVERIFIED",
        "description": "Public geological summaries and technical updates"
    },
    {
        "source_name": "Oil India Limited Public News & Technical Updates",
        "source_url": "https://www.oil-india.com/Media/PressRelease",
        "source_type": "web",
        "access_method": "requests",
        "last_checked": datetime.utcnow().isoformat(),
        "status": "UNVERIFIED",
        "description": "Public press releases and field developments"
    },
    {
        "source_name": "PPAC India Public Petroleum Statistics",
        "source_url": "https://www.ppac.gov.in/",
        "source_type": "web",
        "access_method": "requests",
        "last_checked": datetime.utcnow().isoformat(),
        "status": "UNVERIFIED",
        "description": "Public production and exploration statistics"
    }
]

class SourceRegistry:
    def __init__(self, registry_path: str = SOURCE_REGISTRY_FILE):
        self.registry_path = registry_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SOURCES, f, indent=2)

    def get_all_sources(self) -> List[Dict[str, Any]]:
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_source_status(self, source_name: str, status: str):
        sources = self.get_all_sources()
        for src in sources:
            if src["source_name"] == source_name:
                src["status"] = status
                src["last_checked"] = datetime.utcnow().isoformat()
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(sources, f, indent=2)