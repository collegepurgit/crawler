"""Reusable logging bootstrap helpers."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(log_path: str, level: int = logging.INFO) -> None:
    """Configure root logging to file + console for non-Scrapy scripts."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
