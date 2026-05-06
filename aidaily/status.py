"""Runtime status file for health / stale checks."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .config import BASE_DIR, BEIJING_TZ, STATUS_FILENAME


def write_site_status(
    data: dict[str, Any],
    *,
    date_str: str,
    raw_item_total: int,
    site_total: int,
    max_site_items: int,
) -> None:
    obj = {
        "v": 1,
        "generated_at": datetime.now(BEIJING_TZ).replace(microsecond=0).isoformat(),
        "issue_date": date_str,
        "site_total_items": site_total,
        "raw_item_total": raw_item_total,
        "max_site_items_cap": max_site_items,
        "sources": (data.get("sources") or "").strip(),
    }
    p = BASE_DIR / STATUS_FILENAME
    p.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote: {p}")
