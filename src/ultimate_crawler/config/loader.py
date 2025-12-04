# src/ultimate_crawler/config/loader.py

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import yaml


@dataclass
class LimitsConfig:
    max_domains: int
    max_pages: int
    memory_limit_mb: int
    max_pages_per_domain: int


@dataclass
class CrawlerConfig:
    user_agent: str
    max_concurrent_requests: int
    request_timeout: int
    obey_robots_txt: bool
    politeness_delay: float


@dataclass
class RelevanceConfig:
    min_chars: int
    relevance_threshold: float
    model: str  # "keyword" | "embedding"
    embedding_model_name: Optional[str] = None


@dataclass
class OutputConfig:
    dir: Path
    raw_pages_file: str
    filtered_docs_file: str


@dataclass
class JobConfig:
    job_name: str
    keywords: List[str]
    languages: List[str]
    limits: LimitsConfig
    crawler: CrawlerConfig
    relevance: RelevanceConfig
    output: OutputConfig
    seeds: List[str] = field(default_factory=list)


def load_job_config(path: str) -> JobConfig:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    limits = LimitsConfig(**cfg["limits"])
    crawler = CrawlerConfig(**cfg["crawler"])
    relevance = RelevanceConfig(**cfg["relevance"])
    out_cfg = cfg["output"]
    output = OutputConfig(
        dir=Path(out_cfg["dir"]),
        raw_pages_file=out_cfg["raw_pages_file"],
        filtered_docs_file=out_cfg["filtered_docs_file"],
    )

    seeds = cfg.get("seeds", [])

    return JobConfig(
        job_name=cfg["job_name"],
        keywords=cfg["keywords"],
        languages=cfg["languages"],
        limits=limits,
        crawler=crawler,
        relevance=relevance,
        output=output,
        seeds=seeds,
    )
