"""Load, cap, and export daily_data.json slices."""
from __future__ import annotations

import json
import os
import random
from typing import Any

from .config import BASE_DIR, BEIJING_TZ, DATA_FILE
from .constants import DEFAULT_MAX_SITE_ITEMS, SECTION_KEYS


def current_beijing_date_str() -> str:
    from datetime import datetime

    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")


def get_issue_date(data: dict[str, Any]) -> str:
    return str(data.get("date") or current_beijing_date_str())


def resolve_max_site_items(cli_max: int | None = None) -> int:
    if cli_max is not None:
        return max(1, min(int(cli_max), 500))
    raw = os.environ.get("AI_DAILY_MAX_SITE_ITEMS", "").strip()
    if raw:
        try:
            return max(1, min(int(raw), 500))
        except ValueError:
            pass
    return DEFAULT_MAX_SITE_ITEMS


def load_data() -> dict[str, Any]:
    with open(DATA_FILE) as f:
        return json.load(f)


def _github_display_rng(data: dict[str, Any]) -> random.Random:
    return random.Random(f"github|{get_issue_date(data)}|v1")


def apply_github_display_order(data: dict[str, Any]) -> dict[str, Any]:
    """将 github 列表按固定种子乱序，用于展示/配图，不依赖热门度排序。"""
    g = data.get("github")
    if not g:
        return data
    out = dict(data)
    g2 = list(g)
    _github_display_rng(data).shuffle(g2)
    out["github"] = g2
    return out


def fair_section_quotas(counts: dict[str, int], cap: int) -> dict[str, int]:
    total = sum(counts.get(k, 0) for k in SECTION_KEYS)
    if total <= cap:
        return {k: counts.get(k, 0) for k in SECTION_KEYS}
    res = {k: 0 for k in SECTION_KEYS}
    for _ in range(min(cap, total)):
        eligible = [k for k in SECTION_KEYS if res[k] < counts.get(k, 0)]
        if not eligible:
            break
        k_pick = min(eligible, key=lambda k: (res[k], SECTION_KEYS.index(k)))
        res[k_pick] += 1
    return res


def cap_data_for_site(
    data: dict[str, Any], max_items: int | None = None
) -> dict[str, Any]:
    if max_items is None:
        max_items = DEFAULT_MAX_SITE_ITEMS
    counts = {k: len(data.get(k) or []) for k in SECTION_KEYS}
    total = sum(counts.values())
    if total <= max_items:
        return apply_github_display_order(data)
    quotas = fair_section_quotas(counts, max_items)
    out = dict(data)
    for k in SECTION_KEYS:
        row = data.get(k) or []
        if k == "github":
            row = list(row)
            _github_display_rng(data).shuffle(row)
            out[k] = row[: quotas[k]]
        else:
            out[k] = row[: quotas[k]]
    return out


def make_item_share_href(date_str: str, section_key: str, item_index: int) -> str:
    from .constants import SECTION_KEY_TO_INDEX

    s = SECTION_KEY_TO_INDEX[section_key]
    return f"/share.html?k={date_str}&s={s}&i={item_index}"


def write_issue_data_json(data: dict[str, Any], date_str: str) -> None:
    out_dir = BASE_DIR / "issue-data"
    out_dir.mkdir(exist_ok=True)
    sections = {}
    for k in SECTION_KEYS:
        rows = data.get(k) or []
        sections[k] = [
            {
                "t": (it.get("title") or "Untitled").strip() or "Untitled",
                "s": (it.get("summary_zh") or it.get("summary") or "").strip(),
                "u": (it.get("url") or "#").strip() or "#",
            }
            for it in rows
        ]
    obj = {"date": date_str, "v": 1, "sections": sections}
    p = out_dir / f"{date_str}.json"
    p.write_text(
        json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote: {p}")
