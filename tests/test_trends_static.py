"""Static regression tests for the value-trends pages."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_trends_pages_do_not_ship_template_tokens() -> None:
    token_markers = (
        "DATEDISP",
        "STATTODAY",
        "STATDIRS",
        "STATRADAR",
        "__RADAR_DATE__",
        "__RADAR_DATE_EN__",
        "__NEXT_UPDATE__",
    )

    for page_name in ("trends-today.html", "trends.html"):
        html = (REPO_ROOT / page_name).read_text(encoding="utf-8")
        leaked = [token for token in token_markers if token in html]
        assert leaked == [], f"{page_name} contains unreplaced template tokens: {leaked}"


def test_trends_radar_has_script_language_controls() -> None:
    html = (REPO_ROOT / "trends.html").read_text(encoding="utf-8")

    assert 'id="tr-lang-zh"' in html
    assert 'id="tr-lang-en"' in html
