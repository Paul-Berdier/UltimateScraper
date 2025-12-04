# src/ultimate_crawler/discovery/domain_selector.py

from typing import List, Set
from urllib.parse import urlparse

from ..config.loader import JobConfig
from .search_api import DummySearchEngine, SearchResult


def normalize_domain(url: str) -> str:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def build_seed_urls(cfg: JobConfig) -> List[str]:
    """
    Construit la liste initiale d'URLs à partir :
    - de cfg.seeds si fourni
    - sinon, d'un moteur de recherche externe (Dummy pour l'instant)
    """
    seeds: List[str] = []
    seen_domains: Set[str] = set()

    # 1) Seeds explicites dans la config
    for s in cfg.seeds:
        domain = normalize_domain(s)
        if domain not in seen_domains:
            seen_domains.add(domain)
            seeds.append(s)

    if seeds:
        return seeds

    # 2) Sinon, fallback sur un moteur de recherche externe (Dummy ici)
    engine = DummySearchEngine()
    for lang in cfg.languages:
        for kw in cfg.keywords:
            query = f"{kw}"
            results: List[SearchResult] = engine.search(query, lang, num_results=20)
            for r in results:
                domain = normalize_domain(r.url)
                if domain in seen_domains:
                    continue
                seen_domains.add(domain)
                seeds.append(r.url)
                if len(seeds) >= cfg.limits.max_domains:
                    break
            if len(seeds) >= cfg.limits.max_domains:
                break
        if len(seeds) >= cfg.limits.max_domains:
            break

    return seeds
