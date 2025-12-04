# src/ultimate_crawler/crawl/html_storage.py

from pathlib import Path
import hashlib


class HTMLStorage:
    """
    Optionnel : stocker des snapshots HTML pour debug.
    Ici on stocke dans data/jobs/<job>/html_snapshots/.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, url: str, html: str):
        h = hashlib.md5(url.encode("utf-8")).hexdigest()
        path = self.base_dir / f"{h}.html"
        path.write_text(html, encoding="utf-8")
