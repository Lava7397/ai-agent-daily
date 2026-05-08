"""Unit tests for aidaily.data (caps, quotas, share hrefs)."""

from __future__ import annotations

import importlib
import json
from pathlib import Path


def test_fair_section_quotas_under_cap() -> None:
    from aidaily.data import fair_section_quotas
    from aidaily.constants import SECTION_KEYS

    counts = {k: 5 for k in SECTION_KEYS}
    q = fair_section_quotas(counts, 100)
    assert q == counts


def test_fair_section_quotas_splits_when_over_cap() -> None:
    from aidaily.data import fair_section_quotas
    from aidaily.constants import SECTION_KEYS

    counts = {"research": 10, "github": 8, "models": 6, "community": 4}
    cap = 15
    q = fair_section_quotas(counts, cap)
    assert sum(q.values()) == cap
    for k in SECTION_KEYS:
        assert q[k] <= counts[k]


def test_cap_data_for_site_no_trim_when_small() -> None:
    from aidaily.data import cap_data_for_site

    data = {
        "date": "2099-01-01",
        "research": [{"title": "R", "summary": "s", "url": "u"}],
        "github": [],
        "models": [],
        "community": [],
    }
    out = cap_data_for_site(data, max_items=20)
    assert len(out["research"]) == 1


def test_cap_data_for_site_trims_and_shuffles_github_deterministically() -> None:
    from aidaily.data import cap_data_for_site

    gh = [{"title": f"g{i}", "summary": "", "url": f"https://e/{i}"} for i in range(10)]
    data = {
        "date": "2030-06-01",
        "research": [{"title": "R", "summary": "", "url": ""}],
        "github": gh,
        "models": [{"title": f"m{i}", "summary": "", "url": ""} for i in range(10)],
        "community": [{"title": f"c{i}", "summary": "", "url": ""} for i in range(10)],
    }
    out = cap_data_for_site(data, max_items=12)
    assert sum(len(out[k]) for k in ("research", "github", "models", "community")) == 12
    out2 = cap_data_for_site(data, max_items=12)
    assert out["github"] == out2["github"]


def test_resolve_max_site_items_cli_and_env(monkeypatch) -> None:
    from aidaily.data import resolve_max_site_items

    assert resolve_max_site_items(7) == 7
    assert resolve_max_site_items(9999) == 500
    monkeypatch.setenv("AI_DAILY_MAX_SITE_ITEMS", "33")
    assert resolve_max_site_items(None) == 33


def test_get_issue_date_uses_payload() -> None:
    from aidaily.data import get_issue_date

    assert get_issue_date({"date": "2028-12-31"}) == "2028-12-31"


def test_make_item_share_href() -> None:
    from aidaily.data import make_item_share_href

    assert (
        make_item_share_href("2026-01-02", "github", 3)
        == "/share.html?k=2026-01-02&s=1&i=3"
    )


def test_write_issue_data_json_roundtrip(monkeypatch, tmp_path: Path) -> None:
    from aidaily import data as data_mod

    monkeypatch.setenv("AI_DAILY_BASE_DIR", str(tmp_path))
    import aidaily.config as cfg

    importlib.reload(cfg)
    importlib.reload(data_mod)

    payload = {
        "research": [{"title": "T", "summary_zh": "Z", "url": "https://u"}],
        "github": [],
        "models": [],
        "community": [],
    }
    data_mod.write_issue_data_json(payload, "2099-12-01")
    j = json.loads((tmp_path / "issue-data" / "2099-12-01.json").read_text(encoding="utf-8"))
    assert j["date"] == "2099-12-01"
    assert j["sections"]["research"][0]["t"] == "T"

    monkeypatch.delenv("AI_DAILY_BASE_DIR", raising=False)
    importlib.reload(cfg)
    importlib.reload(data_mod)
