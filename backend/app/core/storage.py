import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

METADATA_FILE = "data/raw/metadata.json"
RAW_STORAGE_DIR = "data/raw"

class StorageManager:
    def __init__(self, base_dir: str = RAW_STORAGE_DIR, metadata_file: str = METADATA_FILE):
        self.base_dir = base_dir
        self.metadata_file = metadata_file
        self._initialize_storage()

    def _initialize_storage(self):
        os.makedirs(os.path.join(self.base_dir, "pdf"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "csv"), exist_ok=True)
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

    def calculate_sha256(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _get_metadata(self) -> Dict[str, Any]:
        with open(self.metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_metadata(self, metadata: Dict[str, Any]):
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def save_raw_file(
        self,
        file_content: bytes,
        file_name: str,
        file_type: str,
        source_url: Optional[str] = None,
        source_name: str = "USER_UPLOAD"
    ) -> Dict[str, Any]:
        sha256_hash = self.calculate_sha256(file_content)
        metadata = self._get_metadata()

        if sha256_hash in metadata:
            return metadata[sha256_hash]

        subfolder = "pdf" if file_type.lower() == "pdf" else "csv"
        safe_filename = f"{sha256_hash[:16]}_{file_name}"
        local_path = os.path.join(self.base_dir, subfolder, safe_filename)

        with open(local_path, "wb") as f:
            f.write(file_content)

        record = {
            "document_id": len(metadata) + 1,
            "file_name": file_name,
            "source_url": source_url,
            "source_name": source_name,
            "download_date": datetime.utcnow().isoformat(),
            "file_type": file_type.upper(),
            "sha256": sha256_hash,
            "local_path": local_path
        }

        metadata[sha256_hash] = record
        self._save_metadata(metadata)
        return record