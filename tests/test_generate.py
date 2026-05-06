"""Smoke tests for generate.py (isolated site root via AI_DAILY_BASE_DIR)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_generate_smoke(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    shutil.copy(
        REPO_ROOT / "tests" / "fixtures" / "daily_data.sample.json",
        site / "daily_data.json",
    )
    shutil.copy(REPO_ROOT / "home.html", site / "home.html")
    (site / "archives").mkdir()

    env = {**os.environ, "AI_DAILY_BASE_DIR": str(site)}
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "generate.py"),
            "--no-compress-archives",
            "--max-site-items",
            "20",
        ],
        env=env,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr

    today = (site / "today.html").read_text(encoding="utf-8")
    assert 'class="card-title"' in today
    assert "section-research" in today
    assert "section-github" in today

    status = json.loads((site / "status.json").read_text(encoding="utf-8"))
    assert status["v"] == 1
    assert status["issue_date"] == "2099-01-15"
    assert status["site_total_items"] == 4
    assert status["raw_item_total"] == 4

    assert (site / "issue-data" / "2099-01-15.json").is_file()
    assert (site / "archives" / "2099-01-15.html").is_file()
    all_archives = (site / "home.html").read_text(encoding="utf-8")
    assert "2099-01-15" in all_archives
