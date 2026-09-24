import os
import json
from datetime import datetime
from app.scraper.base_scraper import BaseScraper

class PDFDownloader(BaseScraper):
    def __init__(self, download_dir: str = "data/raw/pdf", metadata_path: str = "data/raw/metadata.json"):
        super().__init__()
        self.download_dir = download_dir
        self.metadata_path = metadata_path
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)

    def _load_metadata(self) -> dict:
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_metadata(self, metadata: dict):
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def download_pdf(self, url: str, source_name: str) -> str:
        content = self.fetch_url(url)
        sha256 = self.compute_hash(content)
        
        metadata = self._load_metadata()
        if sha256 in metadata:
            print(f"Skipping download. Document already exists with SHA256: {sha256}")
            return metadata[sha256]["local_path"]

        filename = f"{sha256[:12]}.pdf"
        local_path = os.path.join(self.download_dir, filename)

        with open(local_path, "wb") as f:
            f.write(content)

        metadata[sha256] = {
            "document_id": len(metadata) + 1,
            "source_url": url,
            "source_name": source_name,
            "download_date": datetime.utcnow().isoformat(),
            "file_type": "PDF",
            "sha256": sha256,
            "local_path": local_path
        }
        self._save_metadata(metadata)
        return local_path