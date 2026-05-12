"""Static smoke tests for the promoted value-trends pages."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_site_file(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


def test_promoted_trends_brief_contains_papers() -> None:
    home = _read_site_file("home.html")

    assert 'href="trends-today.html"' in home
    assert 'class="tt-paper"' in _read_site_file("trends-today.html")


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
