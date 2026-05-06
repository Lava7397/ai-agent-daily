"""Convert compact issue-data/*.json back into a daily_data-shaped dict for build_html."""
from __future__ import annotations

from typing import Any

from .constants import SECTION_KEYS


def issue_data_json_to_daily(obj: dict[str, Any]) -> dict[str, Any]:
    date_str = str(obj.get("date") or "").strip()
    sections = obj.get("sections") if isinstance(obj.get("sections"), dict) else {}
    out: dict[str, Any] = {
        "date": date_str,
        "sources": (obj.get("sources") or "").strip(),
        "description": (obj.get("description") or "AI Agent 领域最新情报").strip(),
    }
    for k in SECTION_KEYS:
        rows = sections.get(k) if isinstance(sections.get(k), list) else []
        out[k] = []
        for it in rows:
            if not isinstance(it, dict):
                continue
            t = (it.get("t") or "").strip()
            s = (it.get("s") or "").strip()
            u = (it.get("u") or "#").strip() or "#"
            out[k].append(
                {
                    "title": t or "Untitled",
                    "summary": s,
                    "summary_zh": s,
                    "url": u,
                    "tags": [],
                }
            )
    return out
