#!/usr/bin/env python
import argparse

from ultimate_crawler.config.loader import load_job_config
from ultimate_crawler.crawl.fetcher import Fetcher
from ultimate_crawler.crawl.parser import html_to_text
from ultimate_crawler.relevance.language import detect_lang
from ultimate_crawler.relevance.embedding_model import EmbeddingRelevanceModel
from ultimate_crawler.relevance.embedding_filter import EmbeddingRelevanceFilter
from ultimate_crawler.io.logging_setup import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Debug pipeline on a single URL.")
    parser.add_argument("-c", "--config", required=True, help="Job config YAML")
    parser.add_argument("-u", "--url", required=True, help="URL to test")
    args = parser.parse_args()

    cfg = load_job_config(args.config)
    setup_logging()

    fetcher = Fetcher(cfg.crawler)
    html = fetcher.fetch(args.url)
    if not html:
        print("[ERROR] Failed to fetch URL.")
        return

    text = html_to_text(html, url=args.url)
    print(f"[INFO] Extracted text length: {len(text)} chars")

    lang = detect_lang(text)
    print(f"[INFO] Detected language: {lang}")

    emb_model = EmbeddingRelevanceModel(cfg.relevance.embedding_model_name, cfg.keywords)
    relevance = EmbeddingRelevanceFilter(emb_model)

    score = relevance.score(text)
    print(f"[INFO] Relevance score: {score:.4f}")


if __name__ == "__main__":
    main()
