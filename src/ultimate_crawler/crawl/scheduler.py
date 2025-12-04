# src/ultimate_crawler/crawl/scheduler.py

from typing import Iterable, List
from urllib.parse import urlparse
from collections import defaultdict


class Scheduler:
    """
    Scheduler minimal :
    - limite le nombre de pages par domaine
    - peut être enrichi plus tard pour gérer la priorité, profondeur, etc.
    """

    def __init__(self, max_pages_per_domain: int):
        self.max_pages_per_domain = max_pages_per_domain
        self.domain_counts = defaultdict(int)

    def can_crawl(self, url: str) -> bool:
        domain = urlparse(url).netloc
        return self.domain_counts[domain] < self.max_pages_per_domain

    def mark_crawled(self, url: str):
        domain = urlparse(url).netloc
        self.domain_counts[domain] += 1

    def filter_urls(self, urls: Iterable[str]) -> List[str]:
        allowed = []
        for url in urls:
            if self.can_crawl(url):
                allowed.append(url)
        return allowed
