#!/usr/bin/env python
import argparse
import logging

from ultimate_crawler.config.loader import load_job_config
from ultimate_crawler.discovery.domain_selector import build_seed_urls
from ultimate_crawler.core.job_runner import JobRunner
from ultimate_crawler.io.logging_setup import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Run ultimate crawl job.")
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to job config YAML (e.g. configs/job_wine.yaml)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    args = parser.parse_args()

    # Logging
    level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=level)
    logger = logging.getLogger(__name__)

    cfg = load_job_config(args.config)
    logger.info("=== Job: %s ===", cfg.job_name)

    logger.info(
        "Config: keywords=%s | languages=%s | limits: max_domains=%d, max_pages=%d, memory_limit_mb=%d",
        cfg.keywords,
        cfg.languages,
        cfg.limits.max_domains,
        cfg.limits.max_pages,
        cfg.limits.memory_limit_mb,
    )

    seed_urls = build_seed_urls(cfg)
    if not seed_urls:
        logger.warning("No seeds found. Check config (keywords / seeds / search API).")
        return

    logger.info("Seeds found: %d", len(seed_urls))
    for u in seed_urls[:10]:
        logger.debug("Seed: %s", u)

    runner = JobRunner(cfg)
    runner.run(seed_urls)

    logger.info("Job finished.")
    logger.info(
        "Metrics: pages_fetched=%d | pages_kept=%d | bytes_written=%.2f MB | duration=%.1f s",
        runner.metrics.pages_fetched,
        runner.metrics.pages_kept,
        runner.metrics.total_bytes_written / (1024 * 1024),
        runner.metrics.duration_sec,
    )


if __name__ == "__main__":
    main()
