# src/ultimate_crawler/crawl/frontier.py

from collections import deque
from typing import Deque, Set, Optional


class Frontier:
    """
    File d'URLs simple (BFS).
    Plus tard tu pourras ajouter des priorités, scoring, etc.
    """

    def __init__(self):
        self._queue: Deque[str] = deque()
        self._seen: Set[str] = set()

    def add(self, url: str):
        if url not in self._seen:
            self._seen.add(url)
            self._queue.append(url)

    def extend(self, urls):
        for url in urls:
            self.add(url)

    def pop(self) -> Optional[str]:
        if not self._queue:
            return None
        return self._queue.popleft()

    def __len__(self) -> int:
        return len(self._queue)
