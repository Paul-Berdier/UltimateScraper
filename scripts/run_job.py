#!/usr/bin/env python
import argparse

from src.ultimate_crawler.config.loader import load_job_config
from src.ultimate_crawler.discovery.domain_selector import build_seed_urls
from src.ultimate_crawler.core.job_runner import JobRunner


def main():
    parser = argparse.ArgumentParser(description="Run ultimate crawl job.")
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to job config YAML (e.g. configs/job_wine.yaml)"
    )
    args = parser.parse_args()

    cfg = load_job_config(args.config)
    print(f"=== Job: {cfg.job_name} ===")

    seed_urls = build_seed_urls(cfg)
    if not seed_urls:
        print("[WARN] No seeds found. Check config (keywords / seeds / search API).")
        return

    print(f"[INFO] Seeds found: {len(seed_urls)}")
    runner = JobRunner(cfg)
    runner.run(seed_urls)
    print("[INFO] Job finished.")


if __name__ == "__main__":
    main()
