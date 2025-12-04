# src/ultimate_crawler/core/job_runner.py

import json
from pathlib import Path
from urllib.parse import urlparse

from ..config.loader import JobConfig
from ..crawl.frontier import Frontier
from ..crawl.scheduler import Scheduler
from ..crawl.fetcher import Fetcher
from ..crawl.parser import html_to_text
from ..crawl.robots import RobotsManager
from ..relevance.language import detect_lang
from ..relevance.keyword_filter import KeywordRelevanceFilter
from ..relevance.embedding_model import EmbeddingRelevanceModel
from ..relevance.embedding_filter import EmbeddingRelevanceFilter
from ..io.writers import RotatingJSONLWriter
from .metrics import CrawlMetrics
from .utils import estimate_bytes


class JobRunner:
    def __init__(self, cfg: JobConfig):
        self.cfg = cfg

        self.fetcher = Fetcher(cfg.crawler)
        self.robots = RobotsManager(cfg.crawler.user_agent)
        self.scheduler = Scheduler(cfg.limits.max_pages_per_domain)

        if cfg.relevance.model == "keyword":
            self.relevance = KeywordRelevanceFilter(cfg.keywords)
        elif cfg.relevance.model == "embedding":
            emb_model = EmbeddingRelevanceModel(cfg.relevance.embedding_model_name, cfg.keywords)
            self.relevance = EmbeddingRelevanceFilter(emb_model)
        else:
            raise ValueError(f"Unknown relevance model: {cfg.relevance.model}")

        out_dir: Path = cfg.output.dir
        out_dir.mkdir(parents=True, exist_ok=True)

        self.raw_writer = RotatingJSONLWriter(out_dir / cfg.output.raw_pages_file)
        self.filtered_writer = RotatingJSONLWriter(out_dir / cfg.output.filtered_docs_file)

        self.metrics = CrawlMetrics()
        self.visited_urls: set[str] = set()
        self.domains_seen: set[str] = set()

    def _memory_limit_reached(self) -> bool:
        mb = self.metrics.total_bytes_written / (1024 * 1024)
        return mb >= self.cfg.limits.memory_limit_mb

    def run(self, seed_urls):
        frontier = Frontier()
        frontier.extend(seed_urls)

        while len(frontier) > 0:
            if self.metrics.pages_fetched >= self.cfg.limits.max_pages:
                break
            if self._memory_limit_reached():
                break
            if len(self.domains_seen) >= self.cfg.limits.max_domains:
                break

            url = frontier.pop()
            if url is None:
                break
            if url in self.visited_urls:
                continue
            self.visited_urls.add(url)

            if not self.robots.allowed(url) and self.cfg.crawler.obey_robots_txt:
                continue
            if not self.scheduler.can_crawl(url):
                continue

            html = self.fetcher.fetch(url)
            if not html:
                continue

            self.metrics.pages_fetched += 1
            self.scheduler.mark_crawled(url)

            parsed = urlparse(url)
            self.domains_seen.add(parsed.netloc)

            text = html_to_text(html, url=url)
            if not text or len(text) < self.cfg.relevance.min_chars:
                continue

            lang = detect_lang(text)
            if self.cfg.languages and lang not in self.cfg.languages:
                continue

            score = self.relevance.score(text)
            if score < self.cfg.relevance.relevance_threshold:
                continue

            # RAW
            raw_obj = {
                "url": url,
                "domain": parsed.netloc,
                "lang": lang,
                "text": text,
            }
            raw_line = json.dumps(raw_obj, ensure_ascii=False) + "\n"
            self.raw_writer.write(raw_line)

            # FILTERED
            filt_obj = {
                "url": url,
                "domain": parsed.netloc,
                "lang": lang,
                "text": text,
                "score_relevance": score,
            }
            filt_line = json.dumps(filt_obj, ensure_ascii=False) + "\n"
            self.filtered_writer.write(filt_line)

            self.metrics.pages_kept += 1
            self.metrics.total_bytes_written += estimate_bytes(filt_line)

        self.metrics.finish()
        self.raw_writer.close()
        self.filtered_writer.close()
