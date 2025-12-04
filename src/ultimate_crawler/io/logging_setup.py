# src/ultimate_crawler/io/logging_setup.py

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure le logging global du projet.

    - Format: timestamp, niveau, logger, message
    - Sortie: stdout
    """
    root = logging.getLogger()
    # Si déjà configuré, on n'empile pas 36 handlers
    if root.handlers:
        root.setLevel(level)
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root.addHandler(handler)
    root.setLevel(level)
