"""Configure privacy-conscious application logging."""

from __future__ import annotations

import logging
import sys


def configure_logging() -> None:
    """Log operational events to stderr without record values or exception text."""
    logger = logging.getLogger("telix")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
