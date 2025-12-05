# src/ultimate_crawler/distributed/pool_runner.py

from __future__ import annotations

import multiprocessing as mp
from pathlib import Path
from typing import List
import logging

from ..config.loader import JobConfig
from ..discovery.domain_selector import build_seed_urls
from ..core.job_runner import JobRunner

logger = logging.getLogger(__name__)


def _run_shard(job_cfg: JobConfig, shard_id: int, seeds: List[str]) -> None:
    # On clone un output dir spécifique par shard
    shard_dir = Path(job_cfg.output.dir) / f"shard_{shard_id}"
    shard_cfg = job_cfg
    shard_cfg.output.dir = shard_dir  # type: ignore[attr-defined]

    logger.info("Shard %d: %d seeds -> %s", shard_id, len(seeds), shard_dir)
    runner = JobRunner(shard_cfg)
    runner.run(seeds)


def _split_list(xs: List[str], n: int) -> List[List[str]]:
    k = len(xs)
    if n <= 1 or k <= n:
        return [[x] for x in xs]
    out = [[] for _ in range(n)]
    for i, x in enumerate(xs):
        out[i % n].append(x)
    return out


def run_distributed_job(job_cfg: JobConfig, num_workers: int) -> None:
    seeds = build_seed_urls(job_cfg)
    if not seeds:
        logger.warning("No seeds for distributed job.")
        return

    shards = _split_list(seeds, num_workers)
    logger.info(
        "Launching distributed crawl: %d workers, %d seeds (shards=%s)",
        num_workers,
        len(seeds),
        [len(s) for s in shards],
    )

    ctx = mp.get_context("spawn")
    procs: List[mp.Process] = []

    for shard_id, shard_seeds in enumerate(shards):
        if not shard_seeds:
            continue
        p = ctx.Process(
            target=_run_shard,
            args=(job_cfg, shard_id, shard_seeds),
            daemon=False,
        )
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    logger.info("Distributed job finished. Shards stored under %s", job_cfg.output.dir)
