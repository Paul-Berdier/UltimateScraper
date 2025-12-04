# src/ultimate_crawler/crawl/fetcher.py

import time
from typing import Optional

import requests

from ..config.loader import CrawlerConfig


class Fetcher:
    def __init__(self, cfg: CrawlerConfig):
        self.cfg = cfg
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": cfg.user_agent})

    def fetch(self, url: str) -> Optional[str]:
        try:
            resp = self.session.get(url, timeout=self.cfg.request_timeout)
        except Exception:
            return None

        if resp.status_code >= 400:
            return None

        # politeness
        time.sleep(self.cfg.politeness_delay)
        return resp.text
