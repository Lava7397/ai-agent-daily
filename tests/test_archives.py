"""Unit tests for aidaily.archives (meta extraction, overrides, today sync)."""

from __future__ import annotations

import importlib
from pathlib import Path


def _minimal_archive_html(headline: str, summary_zh: str, total: int) -> str:
    return f"""<!DOCTYPE html><html><head></head><body>
<div id="hero-item-count" data-total-items="{total}"></div>
<main class="container" id="main-content">
<section><div class="card top"><a href="https://x.test/t" class="card-title">{headline}</a>
<p class="card-summary" data-i18n-text="zh">{summary_zh}</p>
</div></section></main></body></html>"""


def test_extract_archive_meta_reads_first_card_in_main(tmp_path: Path) -> None:
    from aidaily.archives import extract_archive_meta

    p = tmp_path / "2099-02-01.html"
    p.write_text(
        _minimal_archive_html(
            "Alpha Title",
            "中文摘要一行。",
            42,
        ),
        encoding="utf-8",
    )
    h, t, s = extract_archive_meta(p)
    assert h == "Alpha Title"
    assert t == "42"
    assert "中文摘要" in s


def test_extract_archive_meta_ignores_css_card_title_selector(tmp_path: Path) -> None:
    from aidaily.archives import extract_archive_meta

    p = tmp_path / "x.html"
    p.write_text(
        """<!DOCTYPE html><html><head><style>
.card-title { font-size: 1rem; }
</style></head><body>
<span id="hero-item-count" data-total-items="3"></span>
<main id="main-content"><a class="card-title" href="#">Real Headline</a>
<p class="card-summary" data-i18n-text="zh">Sum</p>
</main></body></html>""",
        encoding="utf-8",
    )
    h, t, _ = extract_archive_meta(p)
    assert h == "Real Headline"
    assert t == "3"


def test_apply_home_archive_override_patches_single_date() -> None:
    from aidaily.archives import apply_home_archive_override

    rows = [
        ("2026-04-30", "Old H", "10", "Old S"),
        ("2026-04-29", "H2", "11", "S2"),
    ]
    data = {
        "home_archive_override": {
            "date": "2026-04-29",
            "headline": "New headline",
            "total_items": "99",
        }
    }
    out = apply_home_archive_override(rows, data)
    assert out[0] == rows[0]
    assert out[1][0] == "2026-04-29"
    assert out[1][1] == "New headline"
    assert out[1][2] == "99"
    assert out[1][3] == "S2"


def test_replace_between_and_extract_between() -> None:
    from aidaily.archives import extract_between, replace_between

    s = "a<!--X-->inner<!--Y-->b"
    assert extract_between(s, "<!--X-->", "<!--Y-->") == "inner"
    assert replace_between(s, "<!--X-->", "<!--Y-->", "z") == "a<!--X-->z<!--Y-->b"


def test_sync_today_html_from_newest_archive(monkeypatch, tmp_path: Path) -> None:
    """Uses isolated site root; restores aidaily.config after reload."""
    monkeypatch.setenv("AI_DAILY_BASE_DIR", str(tmp_path))
    import aidaily.archives as arch
    import aidaily.config as cfg

    importlib.reload(cfg)
    importlib.reload(arch)

    adir = tmp_path / "archives"
    adir.mkdir()
    (adir / "2026-05-01.html").write_text("<html>older</html>", encoding="utf-8")
    (adir / "2026-05-09.html").write_text("<html>newest</html>", encoding="utf-8")
    arch.sync_today_html_from_newest_archive()
    assert (tmp_path / "today.html").read_text(encoding="utf-8") == "<html>newest</html>"

    monkeypatch.delenv("AI_DAILY_BASE_DIR", raising=False)
    importlib.reload(cfg)
    importlib.reload(arch)
