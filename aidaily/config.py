"""Paths and deployment constants (supports AI_DAILY_BASE_DIR for isolated tests)."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

BEIJING_TZ = timezone(timedelta(hours=8))

REPO_ROOT = Path(__file__).resolve().parent.parent


def _resolve_base_dir() -> Path:
    raw = (os.environ.get("AI_DAILY_BASE_DIR") or "").strip()
    if raw:
        p = Path(raw).expanduser().resolve()
        if p.is_dir():
            return p
    return REPO_ROOT


BASE_DIR = _resolve_base_dir()
DATA_FILE = BASE_DIR / "daily_data.json"
OUTPUT_DIR = BASE_DIR / "archives"
STATUS_FILENAME = "status.json"
TODAY_FILENAME = "today.html"
ISSUES_FILENAME = "issues.html"
SITE_URL = os.environ.get("SITE_URL", "https://lava7397.com")
