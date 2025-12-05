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
        self._playwright_fetcher = None
        logger.info("Fetcher initialized with UA=%s", cfg.user_agent)

    def _get_playwright_fetcher(self):
        if self._playwright_fetcher is None:
            from .playwright_fetcher import PlaywrightFetcher
            self._playwright_fetcher = PlaywrightFetcher(self.cfg)
        return self._playwright_fetcher

    def fetch(self, url: str) -> Optional[str]:
        if getattr(self.cfg, "use_playwright", False):
            logger.debug("Using Playwright for %s", url)
            try:
                return self._get_playwright_fetcher().fetch(url)
            except Exception as e:
                logger.warning("Playwright fetch failed for %s, fallback to requests: %r", url, e)

        logger.debug("Fetching URL via requests: %s", url)
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

        if self.cfg.politeness_delay > 0:
            time.sleep(self.cfg.politeness_delay)
        return resp.text
