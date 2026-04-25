#!/usr/bin/env python3
"""
将根目录 today.html 的顶栏 + 四栏导航样式与结构同步到所有 archives/*.html。

用法（仓库根）: python3 scripts/migrate_archives_chrome.py

依赖标准库。从 today.html 读取 <style>、<header> 后直至 <!-- Hero --> 的骨架
与 <script>（body 内最后一段 i18n），每份归档保留自身的 quick-nav 链接内容。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
TODAY = DIR / "today.html"
ARCHIVES = DIR / "archives"
NAV_PAT = re.compile(r'<nav class="quick-nav"[^>]*>([\s\S]*?)</nav>', re.IGNORECASE)
REMOVE_NAV_PAT = re.compile(
    r'<nav class="quick-nav"[^>]*>[\s\S]*?</nav>\s*', re.IGNORECASE
)
STYLE_PAT = re.compile(r'<style>[\s\S]*?</style>', re.IGNORECASE)
SCRIPT_PAT = re.compile(r'(<script>[\s\S]*?</script>)\s*(?=</body>)', re.IGNORECASE)


def _extract_today() -> tuple[str, str, str]:
    t = TODAY.read_text(encoding="utf-8")
    sm = re.search(r"<style>([\s\S]*?)</style>", t, re.IGNORECASE)
    if not sm:
        raise SystemExit("today.html: no <style> block")
    style = sm.group(1)
    m = re.search(
        r"(<a href=\"#main-content\"[^>]*>[\s\S]*?)(?=\n<!-- Hero -->)", t, re.IGNORECASE
    )
    if not m:
        raise SystemExit("today.html: could not find skip-link … <!-- Hero -->")
    body_prefix = m.group(1) + "\n"
    s_from = t.rfind("<script>")
    s_to = t.rfind("</script>")
    if s_from < 0 or s_to < 0 or s_to < s_from:
        raise SystemExit("today.html: no <script> block before </body>")
    script = t[s_from : s_to + len("</script>")]
    return style, body_prefix, script


def _default_nav_inner() -> str:
    return (
        '  <a class="quick-link" href="#section-research">AI Agent 研究</a>'
        '<a class="quick-link" href="#section-github">GitHub 热门</a>'
        '<a class="quick-link" href="#section-models">模型动态</a>'
        '<a class="quick-link" href="#section-community">社区热议</a>'
    )


def _build_header_from_today(skeleton: str, nav_inner: str) -> str:
    """
    body_prefix 含 skip + header 且 nav 内为占位，这里用 re 替换 quck-nav 内部。
    """
    m = re.search(
        r"(<nav class=\"quick-nav\"[^>]*>)([\s\S]*?)(</nav>)", skeleton, re.IGNORECASE
    )
    if not m:
        raise RuntimeError("skeleton has no <nav class=quick-nav>")
    inner = nav_inner if nav_inner.strip() else _default_nav_inner()
    if not str(inner).strip().startswith(" "):
        inner = "\n  " + inner.strip() + "\n"
    return skeleton[: m.start(2)] + inner + skeleton[m.end(2) :]


def migrate_one(
    path: Path, style: str, body_prefix_skeleton: str, script: str
) -> str | None:
    raw = path.read_text(encoding="utf-8")
    navs = NAV_PAT.findall(raw)
    nav_inner = (navs[0] or "").strip() if navs else _default_nav_inner()

    t = raw
    t = REMOVE_NAV_PAT.sub("", t)
    t = STYLE_PAT.sub(f"<style>\n{style}\n</style>", t, count=1)

    ix = t.find("<!-- Hero -->")
    if ix < 0:
        return "skip: no <!-- Hero -->"

    body_open = re.search(r"<body[^>]*>", t, re.IGNORECASE)
    if not body_open:
        return "skip: no <body>"
    body_end = body_open.end()

    new_inner = _build_header_from_today(body_prefix_skeleton, nav_inner)
    t = t[:body_end] + "\n" + new_inner + t[ix:]

    t, count = SCRIPT_PAT.subn(script, t, count=1)
    if count == 0:
        i = t.lower().rfind("</body>")
        if i < 0:
            return "skip: no </body>"
        t = t[:i] + "\n" + script + "\n\n" + t[i:]

    path.write_text(t, encoding="utf-8")
    return None


def main() -> int:
    if not TODAY.is_file():
        print("Need today.html next to this repo", file=sys.stderr)
        return 1
    style, body_prefix, script = _extract_today()
    if not ARCHIVES.is_dir():
        print("No archives/ directory", file=sys.stderr)
        return 1
    files = sorted(ARCHIVES.glob("????-??-??.html"))
    if not files:
        print("No YYYY-MM-DD.html under archives/", file=sys.stderr)
        return 0
    errors = []
    for p in files:
        err = migrate_one(p, style, body_prefix, script)
        if err:
            errors.append(f"{p.name}: {err}")
        else:
            print(f"OK  {p.name}")
    for e in errors:
        print(e, file=sys.stderr)
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
