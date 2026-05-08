"""Optional structured logging for CLI (generate.py)."""
from __future__ import annotations

import logging
import os


def configure_cli_logging(name: str = "aidaily") -> logging.Logger:
    """If AI_DAILY_LOG_LEVEL is set (e.g. INFO, WARNING, DEBUG), attach basic stderr logging."""
    log = logging.getLogger(name)
    raw = os.environ.get("AI_DAILY_LOG_LEVEL", "").strip().upper()
    if not raw:
        return log
    level = getattr(logging, raw, None)
    if level is None or not isinstance(level, int):
        level = logging.INFO
    if not logging.root.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    log.setLevel(level)
    return log
