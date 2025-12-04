# src/ultimate_crawler/core/metrics.py

import time
from dataclasses import dataclass, field


@dataclass
class CrawlMetrics:
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    pages_fetched: int = 0
    pages_kept: int = 0
    total_bytes_written: int = 0

    def finish(self):
        self.end_time = time.time()

    @property
    def duration_sec(self) -> float:
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
