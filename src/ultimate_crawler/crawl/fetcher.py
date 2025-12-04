# src/ultimate_crawler/crawl/fetcher.py

import time
from typing import Optional

import requests
import logging

from ..config.loader import CrawlerConfig

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self, cfg: CrawlerConfig):
        self.cfg = cfg
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": cfg.user_agent})
        logger.info("Fetcher initialized with UA=%s", cfg.user_agent)

    def fetch(self, url: str) -> Optional[str]:
        logger.debug("Fetching URL: %s", url)
        try:
            resp = self.session.get(url, timeout=self.cfg.request_timeout)
        except Exception as e:
            logger.warning("Request error for %s: %r", url, e)
            return None

        if resp.status_code >= 400:
            logger.info("HTTP %d for %s, skipping.", resp.status_code, url)
            return None

        logger.debug("Fetched %s (%d bytes, status=%d)",
                     url, len(resp.content), resp.status_code)

        # politeness delay
        if self.cfg.politeness_delay > 0:
            time.sleep(self.cfg.politeness_delay)
        return resp.text
