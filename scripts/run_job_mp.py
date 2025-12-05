#!/usr/bin/env python
import argparse
import logging

from ultimate_crawler.config.loader import load_job_config
from ultimate_crawler.io.logging_setup import setup_logging
from ultimate_crawler.distributed import run_distributed_job


def main():
    parser = argparse.ArgumentParser(description="Run ultimate crawl job (multi-process).")
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to job config YAML"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=4,
        help="Number of worker processes."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logs."
    )
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=level)
    logger = logging.getLogger(__name__)

    cfg = load_job_config(args.config)
    logger.info("=== Distributed Job: %s ===", cfg.job_name)

    run_distributed_job(cfg, num_workers=args.workers)


if __name__ == "__main__":
    main()
