#!/usr/bin/env python3
"""Re-render archives/YYYY-MM-DD.html from issue-data/YYYY-MM-DD.json (same pipeline as generate)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from aidaily.archives import sync_today_html_from_newest_archive
from aidaily.config import BASE_DIR, OUTPUT_DIR
from aidaily.data import cap_data_for_site, current_beijing_date_str
from aidaily.issue_bridge import issue_data_json_to_daily
from generate import build_html


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("date", help="Issue date YYYY-MM-DD")
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite a non–tip-issue historical archive (dangerous)",
    )
    p.add_argument(
        "--max-site-items",
        type=int,
        default=500,
        metavar="N",
        help="Cap passed to cap_data_for_site (default 500)",
    )
    args = p.parse_args(argv)
    date_str = args.date.strip()
    issue_path = BASE_DIR / "issue-data" / f"{date_str}.json"
    if not issue_path.is_file():
        print(f"ERROR: missing {issue_path}", file=sys.stderr)
        return 1

    obj = json.loads(issue_path.read_text(encoding="utf-8"))
    data = issue_data_json_to_daily(obj)
    data = cap_data_for_site(data, max_items=max(1, min(int(args.max_site_items), 500)))

    paths = sorted(OUTPUT_DIR.glob("????-??-??.html"), key=lambda p: p.stem)
    tip_stem = paths[-1].stem if paths else None
    today_s = current_beijing_date_str()
    archive_path = OUTPUT_DIR / f"{date_str}.html"
    if (
        archive_path.exists()
        and date_str < today_s
        and tip_stem != date_str
        and not args.force
    ):
        print(
            "ERROR: refusing to overwrite historical archive "
            f"(not tip {tip_stem}); use --force",
            file=sys.stderr,
        )
        return 1

    html = build_html(data)
    archive_path.write_text(html, encoding="utf-8")
    print(f"Wrote: {archive_path}")
    sync_today_html_from_newest_archive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
