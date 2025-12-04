# src/ultimate_crawler/core/job_runner.py

import json
from pathlib import Path
from urllib.parse import urlparse
import logging

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

logger = logging.getLogger(__name__)


class JobRunner:
    def __init__(self, cfg: JobConfig):
        self.cfg = cfg

        logger.info("Initializing JobRunner for job=%s", cfg.job_name)

        self.fetcher = Fetcher(cfg.crawler)
        self.robots = RobotsManager(cfg.crawler.user_agent)
        self.scheduler = Scheduler(cfg.limits.max_pages_per_domain)

        if cfg.relevance.model == "keyword":
            logger.info("Using KeywordRelevanceFilter")
            self.relevance = KeywordRelevanceFilter(cfg.keywords)
        elif cfg.relevance.model == "embedding":
            logger.info(
                "Using EmbeddingRelevanceFilter with model=%s",
                cfg.relevance.embedding_model_name
            )
            emb_model = EmbeddingRelevanceModel(cfg.relevance.embedding_model_name, cfg.keywords)
            self.relevance = EmbeddingRelevanceFilter(emb_model)
        else:
            raise ValueError(f"Unknown relevance model: {cfg.relevance.model}")

        out_dir: Path = cfg.output.dir
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Output directory: %s", out_dir)

        self.raw_writer = RotatingJSONLWriter(out_dir / cfg.output.raw_pages_file)
        self.filtered_writer = RotatingJSONLWriter(out_dir / cfg.output.filtered_docs_file)

        self.metrics = CrawlMetrics()
        self.visited_urls: set[str] = set()
        self.domains_seen: set[str] = set()

    def _memory_limit_reached(self) -> bool:
        mb = self.metrics.total_bytes_written / (1024 * 1024)
        return mb >= self.cfg.limits.memory_limit_mb

    def _global_limits_reached(self) -> bool:
        if self.metrics.pages_fetched >= self.cfg.limits.max_pages:
            logger.info("Stopping: max_pages reached (%d)", self.cfg.limits.max_pages)
            return True
        if self._memory_limit_reached():
            logger.info(
                "Stopping: memory limit reached (%.2f MB / %d MB)",
                self.metrics.total_bytes_written / (1024 * 1024),
                self.cfg.limits.memory_limit_mb,
            )
            return True
        if len(self.domains_seen) >= self.cfg.limits.max_domains:
            logger.info("Stopping: max_domains reached (%d)", self.cfg.limits.max_domains)
            return True
        return False

    def run(self, seed_urls):
        logger.info("Starting crawl with %d seed URLs", len(seed_urls))

        frontier = Frontier()
        frontier.extend(seed_urls)

        while len(frontier) > 0:
            if self._global_limits_reached():
                break

            url = frontier.pop()
            if url is None:
                break
            if url in self.visited_urls:
                logger.debug("Already visited, skipping: %s", url)
                continue
            self.visited_urls.add(url)

            if self.cfg.crawler.obey_robots_txt and not self.robots.allowed(url):
                logger.debug("Disallowed by robots.txt, skipping: %s", url)
                continue
            if not self.scheduler.can_crawl(url):
                logger.debug("Domain page limit reached, skipping: %s", url)
                continue

            logger.info("Crawling URL [%d fetched so far]: %s", self.metrics.pages_fetched, url)
            html = self.fetcher.fetch(url)
            if not html:
                logger.debug("Empty HTML, skipping: %s", url)
                continue

            self.metrics.pages_fetched += 1
            self.scheduler.mark_crawled(url)

            parsed = urlparse(url)
            self.domains_seen.add(parsed.netloc)

            # Extraction texte
            text = html_to_text(html, url=url)
            if not text:
                logger.debug("No text extracted, skipping: %s", url)
                continue
            if len(text) < self.cfg.relevance.min_chars:
                logger.debug(
                    "Text too short (%d chars < min_chars=%d), skipping: %s",
                    len(text),
                    self.cfg.relevance.min_chars,
                    url,
                )
                continue

            # Langue
            lang = detect_lang(text)
            logger.debug("Detected language for %s: %s", url, lang)
            if self.cfg.languages and lang not in self.cfg.languages:
                logger.debug(
                    "Language %s not in allowed list %s, skipping: %s",
                    lang,
                    self.cfg.languages,
                    url,
                )
                continue

            # Pertinence
            score = self.relevance.score(text)
            logger.debug(
                "Relevance score for %s: %.4f (threshold=%.4f)",
                url,
                score,
                self.cfg.relevance.relevance_threshold,
            )
            if score < self.cfg.relevance.relevance_threshold:
                logger.debug("Score below threshold, skipping: %s", url)
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

        logger.info(
            "Crawl finished: pages_fetched=%d, pages_kept=%d, domains_seen=%d, bytes_written=%.2f MB, duration=%.1f s",
            self.metrics.pages_fetched,
            self.metrics.pages_kept,
            len(self.domains_seen),
            self.metrics.total_bytes_written / (1024 * 1024),
            self.metrics.duration_sec,
        )
