# src/ultimate_crawler/crawl/playwright_fetcher.py

from __future__ import annotations

from typing import Optional
import logging
import time

from ..config.loader import CrawlerConfig

logger = logging.getLogger(__name__)


class PlaywrightFetcher:
    """
    Fetcher basé sur Playwright pour rendre du JS.
    Nécessite:
      pip install playwright
      playwright install
    """

    def __init__(self, cfg: CrawlerConfig):
        self.cfg = cfg
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError:
            raise RuntimeError(
                "playwright is not installed. Run `pip install playwright` + `playwright install`."
            )
        self._sync_playwright = sync_playwright
        logger.info("PlaywrightFetcher initialized.")

    def fetch(self, url: str) -> Optional[str]:
        logger.debug("Playwright fetching URL: %s", url)
        with self._sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=self.cfg.user_agent)
            try:
                page.goto(url, timeout=self.cfg.request_timeout * 1000)
                # wait a bit for JS
                time.sleep(2.0)
                content = page.content()
            except Exception as e:
                logger.warning("Playwright error for %s: %r", url, e)
                content = None
            finally:
                browser.close()
        return content
