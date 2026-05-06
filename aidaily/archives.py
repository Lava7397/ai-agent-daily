"""Archive scanning, home-list patching, today sync."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import BASE_DIR, OUTPUT_DIR, TODAY_FILENAME


def sync_today_html_from_newest_archive() -> None:
    paths = sorted(OUTPUT_DIR.glob("????-??-??.html"), key=lambda p: p.stem)
    if not paths:
        return
    latest = paths[-1]
    today_path = BASE_DIR / TODAY_FILENAME
    today_path.write_text(latest.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Synced {TODAY_FILENAME} ← {latest.name} (newest archive)")


def replace_between(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"start marker not found: {start_marker}")
    end = text.find(end_marker, start + len(start_marker))
    if end == -1:
        raise ValueError(f"end marker not found: {end_marker}")
    return text[: start + len(start_marker)] + replacement + text[end:]


def extract_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"start marker not found: {start_marker}")
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"end marker not found: {end_marker}")
    return text[start:end]


def _html_main_content_scope(html: str) -> str:
    m = re.search(
        r'<main\b[^>]*\bid\s*=\s*["\']main-content["\'][^>]*>',
        html,
        re.I,
    )
    if not m:
        return html
    start = m.end()
    end = html.lower().find("</main>", start)
    if end == -1:
        return html[start:]
    return html[start:end]


def extract_archive_meta(archive_path: Path) -> tuple[str, str, str]:
    try:
        raw = archive_path.read_text(encoding="utf-8")
        html = _html_main_content_scope(raw)
        m = re.search(r'<a[^>]+class="card-title"[^>]*>([^<]+)</a>', html)
        headline = m.group(1).strip() if m else ""
        mtot = re.search(
            r'id="hero-item-count"[^>]*data-total-items="(\d+)"',
            raw,
        ) or re.search(r'data-total-items="(\d+)"', raw)
        if mtot:
            total = mtot.group(1)
        else:
            n = re.findall(r'class="stat-num"[^>]*>([\d]+)</div>', raw)
            total = n[0] if n else ""
        summary = ""
        if m:
            after = html[m.end() :]
            sm = re.search(r'<p[^>]*class="card-summary"[^>]*>([^<]+)</p>', after)
            if sm:
                summary = sm.group(1).strip()
        return headline, total, summary
    except Exception:
        return "", "", ""


def apply_home_archive_override(
    archive_infos: list[tuple], data: dict[str, Any]
) -> list[tuple]:
    ov = data.get("home_archive_override")
    if not isinstance(ov, dict):
        return archive_infos
    d0 = ov.get("date")
    if not d0:
        return archive_infos
    h_new = ov.get("headline")
    s_new = ov.get("summary")
    t_new = ov.get("total_items")
    if h_new is None and s_new is None and t_new is None:
        return archive_infos
    out = []
    for row in archive_infos:
        if row[0] != d0:
            out.append(row)
            continue
        h = h_new if h_new is not None else row[1]
        t = t_new if t_new is not None else row[2]
        s = s_new if s_new is not None else row[3]
        out.append((row[0], h, t, s))
    return out


def patch_polished_home_archives_data(
    existing_html: str, archive_infos: list[tuple]
) -> str:
    home_rows = [[row[0], str(row[2])] for row in archive_infos]
    archive_data_block = json.dumps(home_rows, ensure_ascii=False, separators=(",", ":"))
    updated = replace_between(
        existing_html,
        "const ALL_ARCHIVES = ",
        "\n\nconst LANG_STORAGE =",
        archive_data_block,
    )
    print(f"Updated: home.html (ALL_ARCHIVES, {len(archive_infos)} issues)")
    return updated
