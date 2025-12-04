# src/ultimate_crawler/io/logging_setup.py

import logging


def setup_logging(level: int = logging.INFO):
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=level,
    )
