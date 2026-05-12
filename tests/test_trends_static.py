"""Static smoke tests for the promoted value-trends pages."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_site_file(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


def test_promoted_trends_brief_contains_papers() -> None:
    home = _read_site_file("home.html")

    assert 'href="trends-today.html"' in home
    assert 'class="tt-paper"' in _read_site_file("trends-today.html")


def test_trend_metadata_is_consistent_across_static_files() -> None:
    home = _read_site_file("home.html")
    today = _read_site_file("trends-today.html")
    data = json.loads(_read_site_file("trends-data.json"))

    block_match = re.search(
        r"<!-- TECH-TRENDS-CARD-START -->(.*?)<!-- TECH-TRENDS-CARD-END -->",
        home,
        re.S,
    )
    assert block_match is not None
    home_values = re.findall(r'<div class="num(?: [^"]*)?">(.*?)</div>', block_match.group(1))

    assert home_values[:3] == [
        str(data["total_papers"]),
        str(data["direction_count"]),
        data["date"],
    ]
    assert today.count('class="tt-paper"') == data["total_papers"]

    radar_match = re.search(r'id="tt-stat-radar">([^<]+)</div>', today)
    assert radar_match is not None
    assert home_values[3] == radar_match.group(1)


def test_trend_pages_do_not_ship_template_tokens() -> None:
    bad_tokens = (
        "DATEDISP",
        "DATEDISPEN",
        "STATTODAY",
        "STATTODAYEN",
        "STATDIRS",
        "STATDIRSEN",
        "STATRADAR",
        "STATRADAREN",
        "__RADAR_DATE__",
        "__RADAR_DATE_EN__",
        "__NEXT_UPDATE__",
    )

    for filename in ("trends-today.html", "trends.html"):
        html = _read_site_file(filename)
        for token in bad_tokens:
            assert token not in html, f"{filename} contains unreplaced token {token}"


def test_radar_language_controls_match_script_bindings() -> None:
    html = _read_site_file("trends.html")

    assert 'id="tr-lang-zh"' in html
    assert 'id="tr-lang-en"' in html
