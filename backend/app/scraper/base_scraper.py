import time
import hashlib
import requests
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

class BaseScraper:
    def __init__(self, user_agent: str = "eRTMAC-NWIS-Bot/1.0 (+http://oil-india.in)"):
        self.headers = {"User-Agent": user_agent}
        self.timeout = 15

    def can_fetch(self, url: str) -> bool:
        """Check robots.txt compliance before hitting target."""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rfp = RobotFileParser()
        try:
            rfp.set_url(robots_url)
            rfp.read()
            return rfp.can_fetch(self.headers["User-Agent"], url)
        except Exception:
            # If robots.txt cannot be fetched, default to safe policy
            return True

    def compute_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def fetch_url(self, url: str, retries: int = 3, backoff_factor: float = 2.0) -> bytes:
        if not self.can_fetch(url):
            raise PermissionError(f"Scraping blocked by robots.txt for URL: {url}")

        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                return response.content
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                time.sleep(backoff_factor ** attempt)
        raise RuntimeError(f"Failed to fetch {url} after {retries} retries.")