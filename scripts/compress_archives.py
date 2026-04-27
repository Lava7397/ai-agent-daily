#!/usr/bin/env python3
"""
将「北京时间当天」之前的历史 archives/*.html 做安全压缩（收拢标签间空白）。
保留 <script> / <style> 内原文，不删注释，避免破 JS/CSS。

可单独执行：  python3 scripts/compress_archives.py [--dry-run]
由 generate.py 在生成后自动调用。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 成对匹配 script / style，避免在字符串里错误折叠（保守保留整块）
_RE_BLOCK = re.compile(
    r"""(<script\b[^>]*>.*?</script>)|(<style\b[^>]*>.*?</style>)""",
    re.DOTALL | re.IGNORECASE,
)
_RE_BETWEEN_TAGS = re.compile(r">\s+<")


def _minify_html_preserve_blocks(html: str) -> str:
    out: list[str] = []
    i = 0
    for m in _RE_BLOCK.finditer(html):
        if m.start() > i:
            chunk = _RE_BETWEEN_TAGS.sub("><", html[i : m.start()])
            out.append(chunk)
        out.append(m.group(0))
        i = m.end()
    if i < len(html):
        out.append(_RE_BETWEEN_TAGS.sub("><", html[i:]))
    return "".join(out).strip() + "\n"


def compress_historic_archives(
    base_dir: Path,
    beijing_today: str,
    *,
    dry_run: bool = False,
) -> int:
    """
    对 archives/YYYY-MM-DD.html 中 date < beijing_today 的文件做 minify 写回。

    beijing_today: YYYY-MM-DD（与 generate 里 current_beijing_date_str 一致）
    返回被写入/将写入的文件数。
    """
    archives = base_dir / "archives"
    if not archives.is_dir():
        return 0
    n = 0
    for p in sorted(archives.glob("????-??-??.html")):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem):
            continue
        if p.stem >= beijing_today:
            continue
        text = p.read_text(encoding="utf-8")
        new = _minify_html_preserve_blocks(text)
        if new == text:
            continue
        n += 1
        if not dry_run:
            p.write_text(new, encoding="utf-8")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Minify historical archive HTML (exclude BJT today).",
    )
    ap.add_argument(
        "--base",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="project root (parent of archives/)",
    )
    ap.add_argument(
        "--as-of",
        metavar="YYYY-MM-DD",
        default="",
        help="treat as Beijing calendar date (default: now in UTC+8)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="only print how many files would be updated",
    )
    args = ap.parse_args()
    from datetime import datetime, timezone, timedelta

    bj = timezone(timedelta(hours=8))
    if args.as_of:
        today = args.as_of
    else:
        today = datetime.now(bj).strftime("%Y-%m-%d")
    n = compress_historic_archives(args.base, today, dry_run=args.dry_run)
    if args.dry_run:
        print(f"Would update {n} file(s) (as-of BJT {today}).")
    else:
        print(f"Compressed {n} historical archive(s) (as-of BJT {today}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
