#!/usr/bin/env python3
"""
将日刊页（当日刊 + 历史归档）与 generate.py 中 build_html() 输出对齐。

用法（仓库根目录）: python3 scripts/sync_issue_pages.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ARCHIVES = BASE / "archives"
TODAY = BASE / "today.html"

SPLIT_MARKER = "\n/* ---- Quick Nav"

# 与 generate.py 当日输出一致：单块 issue-sticky-dock 顶栏 + Hero/Quick Nav 样式
CANON_STICKY_HERO_QUICKNAV = r"""
/* ---- 日刊头：顶栏 position:fixed（相对视口吸顶，滚入正文时仍不离开顶部；sticky 在部分 WebView 上不可靠）---- */
.detail-issue-top--fixed-dock {
  padding-top: calc(env(safe-area-inset-top, 0px) + var(--issue-dock-row-h));
}
.detail-issue-top--fixed-dock.detail-issue-top--nav-only-bar {
  padding-top: calc(env(safe-area-inset-top, 0px) + var(--issue-dock-navonly-h));
}
.issue-sticky-dock {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  max-width: none;
  margin: 0;
  z-index: 200;
  box-sizing: border-box;
  padding-top: env(safe-area-inset-top, 0px);
  background: rgba(245,240,232,0.95);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(100,80,60,0.1);
  -webkit-transform: translateZ(0);
  transform: translateZ(0);
}
.issue-sticky-dock .detail-topbar {
  max-width: 720px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
.issue-sticky-dock--nav-only {
  border-top: none;
}
.detail-topbar-inner {
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  min-height: 28px;
}
.detail-topbar-inner--with-quicknav {
  flex-wrap: nowrap;
  padding: 6px 8px 6px 10px;
  min-height: 40px;
  gap: 6px;
}
.detail-topbar-inner--nav-only {
  justify-content: center;
  padding: 8px 10px;
}
.detail-topbar-sub {
  width: 100%;
  box-sizing: border-box;
  padding: 4px 12px 6px;
  border-top: none;
}
.atlas-btn {
  flex-shrink: 0;
  border: 1px solid rgba(100,80,60,0.18);
  color: #4d4338;
  background: #f8f4eb;
  text-decoration: none;
  padding: 6px 10px;
  font-size: 10px;
  letter-spacing: 1.1px;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 2px;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: background var(--ix), color var(--ix), border-color var(--ix), box-shadow var(--ix), transform 0.12s ease;
}
.atlas-btn:hover {
  background: #efe6d8;
  border-color: rgba(100, 80, 60, 0.32);
  box-shadow: 0 1px 4px rgba(45, 36, 28, 0.08);
  transform: translateY(-1px);
}
.atlas-btn:active { transform: translateY(0); }
.atlas-btn:focus-visible { outline: 2px solid #98703f; outline-offset: 2px; }
.atlas-lang {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}
.atlas-lang button {
  background: transparent;
  border: none;
  cursor: pointer;
  font: inherit;
  font-size: 11px;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: #6f6559;
  padding: 4px 6px;
  border-radius: 2px;
  transition: color var(--ix), background var(--ix), font-weight 0.1s, transform 0.1s;
}
.atlas-lang button:hover {
  color: #2f2c27;
  background: rgba(100, 80, 60, 0.1);
  transform: translateY(-0.5px);
}
.atlas-lang button:focus-visible { outline: 2px solid #98703f; outline-offset: 1px; }
.atlas-lang button.active {
  color: #2f2c27;
  font-weight: 700;
  background: rgba(100,80,60,0.08);
}
.atlas-lang-sep {
  color: #b0a89a;
  font-size: 11px;
  user-select: none;
}

/* ---- Hero / 莫比斯封面 ---- */
.hero {
  background:
    radial-gradient(ellipse at 20% 80%, rgba(178,200,218,0.35) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(210,185,220,0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(245,235,210,0.5) 0%, transparent 70%),
    #f5f0e8;
  padding: 20px 24px 16px;
  text-align: center;
  position: relative;
  border-bottom: 2px solid rgba(100,80,60,0.15);
}
.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 3px,
    rgba(100,80,60,0.02) 3px, rgba(100,80,60,0.02) 4px
  );
  pointer-events: none;
}
.hero h1 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 38px;
  font-weight: 700;
  color: #3a3a3a;
  letter-spacing: 3px;
  position: relative;
  z-index: 1;
}
.hero .date {
  color: #8a7e6e;
  font-size: 13px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  margin-top: 6px;
  position: relative;
  z-index: 1;
  letter-spacing: 0.5px;
  line-height: 1.5;
}
.hero .date .hero-sep,
.hero .date .hero-tagline,
.hero .date .hero-count,
.hero .date .hero-count-unit {
  font: inherit;
  font-size: inherit;
  line-height: inherit;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.hero .date .hero-sep { color: #b0a89a; margin: 0 0.1em; }
.hero .date .hero-tagline { color: #7a6f62; font-weight: 500; letter-spacing: 0.4px; }
.hero .date .hero-count { font-weight: 600; color: #5a6e8a; margin-left: 0.1em; }
.hero .date .hero-count-unit { color: #6f6559; font-weight: 500; margin-left: 0; }

/* ---- Quick Nav：顶栏内与返回同行时可横向滑动 ---- */
.quick-nav {
  width: 100%;
  min-width: 0;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  gap: 4px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.quick-nav--inline {
  flex: 1 1 0;
  width: auto;
  min-width: 0;
  justify-content: flex-start;
  gap: 3px;
}
.quick-nav::-webkit-scrollbar { display: none; }
.quick-link {
  display: inline-block;
  flex: 0 0 auto;
  white-space: nowrap;
  padding: 5px 8px;
  text-decoration: none;
  color: #5a6e8a;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(90,110,138,0.2);
  font-size: 10px;
  font-family: 'Inter', sans-serif;
  letter-spacing: 0.2px;
  transition: all 0.25s;
}
.detail-topbar-inner--with-quicknav .quick-link {
  padding: 4px 5px;
  font-size: 9px;
  letter-spacing: 0;
}
.quick-link:hover {
  color: #fff;
  background: #5a6e8a;
  border-color: #5a6e8a;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(90, 110, 138, 0.2);
}
.quick-link:focus-visible {
  outline: 2px solid #4a6080;
  outline-offset: 2px;
}
"""

# 到「Container」注释的完整结束 */ 为止（日刊头 / 顶栏 两种历史注释）
RE_STICKY_TO_CONTAINER = re.compile(
    r"/\* ---- (?:日刊头|顶栏)[^\n]*\n[\s\S]*?/\* ---- Container.*?\*/",
    re.DOTALL,
)

RE_TOPBAR_SINGLE_ROW = re.compile(
    r'(<div class="detail-topbar">\s*<div class="detail-topbar-inner">\s*)'
    r'(<a href="home\.html" class="atlas-btn" id="back-home"[\s\S]*?</a>\s*)'
    r'(<nav class="quick-nav"[\s\S]*?</nav>\s*)'
    r'(<div class="atlas-lang"[\s\S]*?</div>\s*)'
    r'(</div>\s*</div>\s*</header>)',
    re.MULTILINE,
)

RE_HERO_DOUBLE_CLOSE = re.compile(
    r'(<p class="date">[\s\S]*?</p>)\n</div>\n</div>(?=\s*[\r\n]+(?:<!--|<main))',
    re.MULTILINE,
)

RE_STATS_INNER = re.compile(
    r"\s*<div class=\"stats\">(?:\s*<div class=\"stat\">[\s\S]*?</div>\s*){3}</div>\s*",
    re.MULTILINE,
)
RE_OLD_HERO_STATS_CSS = re.compile(
    r"\.hero \.stats \{[\s\S]*?\.hero \.stat-label \{[\s\S]*?letter-spacing: 1\.5px;\s*\}\s*",
    re.MULTILINE,
)


def _extract_total_from_stats(html: str) -> int | None:
    s = html.find('<div class="stats">')
    if s < 0:
        return None
    m = re.search(r'<div class="stat-num">(\d+)</div>', html[s : s + 4000])
    return int(m.group(1)) if m else None


def _date_from_hero_p(inner: str) -> str:
    m = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2})", inner)
    return m.group(1) if m else ""


def _patch_i18n_hero(t: str) -> str:
    t = t.replace("hero_subtitle_suffix: '· 每日精选',", "hero_count_unit: '条',")
    t = t.replace("hero_subtitle_suffix: '· Daily picks',", "hero_count_unit: ' items',")
    t = re.sub(
        r"\n\s*stat_(items|sections|sources):\s*'[^']*',", "", t
    )
    t = re.sub(
        r"\n\s*stat_(items|sections|sources):\s*\"[^\"]*\",", "", t
    )
    return t


def _patch_i18n_hero_tagline(t: str) -> str:
    if "hero_tagline:" in t:
        return t
    t = t.replace(
        "      hero_count_unit: '条',",
        "      hero_tagline: '每日精选',\n      hero_count_unit: '条',",
        1,
    )
    t = t.replace(
        "      hero_count_unit: ' items',",
        "      hero_tagline: 'Daily picks',\n      hero_count_unit: ' items',",
        1,
    )
    return t


def _fix_hero_double_close(t: str) -> str:
    m = RE_HERO_DOUBLE_CLOSE.search(t)
    if not m:
        return t
    return t[: m.start()] + m.group(1) + "\n</div>" + t[m.end() :]


def _migrate_topbar_html(t: str) -> str:
    if "detail-topbar-sub" in t:
        return t
    m = RE_TOPBAR_SINGLE_ROW.search(t)
    if not m:
        return t
    replaced = (
        m.group(1)
        + m.group(2)
        + m.group(4)
        + "  </div>\n  <div class=\"detail-topbar-sub\">\n"
        + m.group(3).strip()
        + "\n  </div>\n</div>\n</header>"
    )
    return t[: m.start()] + replaced + t[m.end() :]


def _fix_broken_hero_tagline_escapes(t: str) -> str:
    return t.replace(
        'class=\\"hero-tagline\\" data-i18n=\\"hero_tagline\\"',
        'class="hero-tagline" data-i18n="hero_tagline"',
    )


def _hero_tagline_repl(m: re.Match) -> str:
    return (
        f'{m.group(1)} <span class="hero-tagline" data-i18n="hero_tagline">'
        f'每日精选</span> <span class="hero-sep" aria-hidden="true">·</span> {m.group(2)}'
    )


def _inject_hero_tagline(t: str) -> str:
    t = _fix_broken_hero_tagline_escapes(t)
    if re.search(r'<span class="hero-tagline"', t):
        return t
    return re.sub(
        r'(<span class="hero-sep"[^>]*>·</span>)\s*(<span class="hero-count")',
        _hero_tagline_repl,
        t,
        count=1,
    )


def _reorder_hero_sticky_top(t: str) -> str:
    """极旧：整段 header 内含返回+四格，Hero 在其下 –→ leading + 仅四格 sticky。已用 leading 的页面跳过。"""
    if "detail-page-leading" in t:
        return t
    hdr = re.search(
        r'<header class="detail-sticky-header">[\s\S]*?</header>',
        t,
        re.DOTALL,
    )
    if not hdr or "detail-topbar-sub" not in hdr.group(0):
        return t
    hm = re.search(
        r"<!-- Hero -->\s*<div class=\"hero\">[\s\S]*?</div>\s*",
        t,
        re.DOTALL,
    )
    if not hm:
        return t
    hero_block = re.search(
        r'<div class="hero">[\s\S]*?</div>', hm.group(0), re.DOTALL
    )
    if not hero_block:
        return t
    hero_only = hero_block.group(0)
    ht = hdr.group(0)
    pos = ht.find('<div class="detail-topbar-sub">')
    if pos < 0:
        return t
    pre = ht[:pos]
    i1 = pre.find('<div class="detail-topbar-inner">')
    i2 = pre.rfind("</div>")
    if i1 < 0 or i2 < i1:
        return t
    inner_segment = pre[i1 : i2 + 6]
    sub_m = re.search(
        r'<div class="detail-topbar-sub">[\s\S]*?</div>\s*', ht, re.DOTALL
    )
    if not sub_m:
        return t
    sub_block = sub_m.group(0).rstrip()
    new_top = (
        '<div class="detail-page-leading">\n<div class="detail-topbar">\n'
        + inner_segment
        + "\n</div>\n"
        + hero_only
        + "\n</div>\n<header class=\"detail-sticky-header\">\n"
        + sub_block
        + "\n</header>\n"
    )
    h_s, h_e = hdr.span()
    he_s, he_e = hm.span()
    if h_s > he_s:
        return t
    return t[:h_s] + new_top + t[he_e:]


def _collapse_topbar_to_single_row(t: str) -> str:
    """两行的 detail-topbar + detail-topbar-sub → 同一行 with-quicknav + quick-nav--inline。"""
    if "quick-nav--inline" in t:
        return t
    m = re.search(
        r'(<div class="detail-topbar">\s*<div class="detail-topbar-inner)(">)\s*'
        r'(<a\s[^>]*\batlas-btn\b[^>]*>[\s\S]*?</a>)\s*'
        r'(<div class="atlas-lang"[\s\S]*?</div>)\s*'
        r'</div>\s*</div>\s*<div class="detail-topbar-sub">\s*'
        r'(<nav class="quick-nav"[^>]*>[\s\S]*?</nav>)\s*'
        r'</div>\s*</header>',
        t,
        re.DOTALL,
    )
    if not m:
        return t
    nav = m.group(5)
    if "quick-nav--inline" not in nav:
        nav = re.sub(
            r'class="quick-nav"',
            'class="quick-nav quick-nav--inline"',
            nav,
            count=1,
        )
    return (
        t[: m.start()]
        + f'{m.group(1)} detail-topbar-inner--with-quicknav{m.group(2)}  {m.group(3)}'
        + f"\n  {nav}\n  {m.group(4)}"
        + "\n  </div>\n</div>\n</header>"
        + t[m.end() :]
    )


def _nav_only_sub_to_wrapped_topbar(t: str) -> str:
    """无返回页：detail-topbar-sub 包裹的 nav → detail-topbar + detail-topbar-inner--nav-only。"""
    if "detail-topbar-sub" not in t or "issue-sticky-dock--nav-only" not in t:
        return t
    m = re.search(
        r'(<header class="issue-sticky-dock issue-sticky-dock--nav-only"[^>]*>)\s*'
        r'<div class="detail-topbar-sub">\s*'
        r'(<nav class="quick-nav"[^>]*>[\s\S]*?</nav>)\s*'
        r"</div>\s*</header>",
        t,
        re.DOTALL,
    )
    if not m:
        return t
    return (
        t[: m.start()]
        + f'{m.group(1)}\n<div class="detail-topbar">\n  '
        f'<div class="detail-topbar-inner detail-topbar-inner--nav-only">\n  {m.group(2)}'
        + "\n  </div>\n</div>\n</header>"
        + t[m.end() :]
    )


def _merge_dual_sticky_to_issue_dock(t: str) -> str:
    """旧版双 header 吸顶 + Hero 夹中间 → 单块 issue-sticky-dock，Hero 在下方。"""
    if "issue-sticky-dock" in t:
        return t
    if "detail-sticky-bar--back" not in t:
        return t
    m = re.search(
        r'(<div class="detail-issue-top">)\s*'
        r'<header class="detail-sticky-bar detail-sticky-bar--back"[^>]*>([\s\S]*?)</header>\s*'
        r'(<div class="hero">[\s\S]*?</div>\s*)'
        r'<header class="detail-sticky-bar detail-sticky-bar--quicknav"[^>]*>([\s\S]*?)</header>\s*'
        r'(</div>)',
        t,
        re.DOTALL,
    )
    if not m:
        return t
    return (
        t[: m.start()]
        + '<div class="detail-issue-top detail-issue-top--fixed-dock">\n'
        + "<header class=\"issue-sticky-dock\" "
        'aria-label="日刊顶栏与栏目导航">\n'
        + m.group(2)
        + m.group(4)
        + "\n</header>\n"
        + m.group(3)
        + m.group(5)
        + t[m.end() :]
    )


def _upgrade_sticky_class_aliases(t: str) -> str:
    """仅四格行 sticky 的旧 class → issue-sticky-dock--nav-only。"""
    if "detail-sticky-bar--quicknav-only" not in t:
        return t
    return t.replace(
        "detail-sticky-bar detail-sticky-bar--quicknav detail-sticky-bar--quicknav-only",
        "issue-sticky-dock issue-sticky-dock--nav-only",
        1,
    )


def _upgrade_leading_to_dual_sticky(t: str) -> str:
    """leading(返回+hero)+单块四格 sticky –→ issue-sticky-dock(返回+四格) + hero。生成物已有则跳过。"""
    if "issue-sticky-dock" in t or "detail-sticky-bar--back" in t or "detail-issue-top" in t:
        return t
    if "detail-page-leading" not in t or "detail-sticky-header" not in t:
        return t
    lead = re.search(
        r'<div class="detail-page-leading">\s*<div class="detail-topbar">[\s\S]*?'
        r"</div>\s*</div>\s*<div class=\"hero\">[\s\S]*?</div>\s*</div>\s*",
        t,
        re.DOTALL,
    )
    if not lead:
        return t
    blob = lead.group(0)
    h0 = blob.find("<div class=\"hero\">")
    if h0 < 0:
        return t
    inner_m = re.search(
        r'<div class="detail-topbar-inner"[^>]*>([\s\S]*?)</div>(?=\s*</div>\s*<div class="hero">)',
        blob,
        re.DOTALL,
    )
    if not inner_m:
        return t
    inner_guts = inner_m.group(1).strip()
    he = re.search(r'<div class="hero">[\s\S]*?</div>\s*', blob, re.DOTALL)
    if not he:
        return t
    hero_only = he.group(0).rstrip()
    hdr = re.search(
        r'<header class="detail-sticky-header">[\s\S]*?</header>\s*',
        t[lead.end() :],
        re.DOTALL,
    )
    if not hdr:
        return t
    sm = re.search(
        r'(<nav class="quick-nav"[^>]*>[\s\S]*?</nav>)',
        hdr.group(0),
        re.DOTALL,
    )
    if not sm:
        return t
    nav_el = sm.group(1)
    if "quick-nav--inline" not in nav_el:
        nav_el = re.sub(
            r'class="quick-nav"',
            'class="quick-nav quick-nav--inline"',
            nav_el,
            count=1,
        )
    new_top = (
        '<div class="detail-issue-top detail-issue-top--fixed-dock">\n'
        '<header class="issue-sticky-dock" aria-label="日刊顶栏与栏目导航">\n'
        '<div class="detail-topbar">\n'
        '  <div class="detail-topbar-inner detail-topbar-inner--with-quicknav">\n  '
        + inner_guts
        + "\n  "
        + nav_el
        + "\n  </div>\n</div>\n</header>\n"
        + hero_only
        + "\n</div>\n"
    )
    a = lead.start()
    d = lead.end() + len(hdr.group(0))
    return t[:a] + new_top + t[d:]


def _replace_sticky_hero_quicksnav_css(t: str) -> str:
    if "/* ---- Container" not in t:
        return t
    if "/* ---- 日刊头" not in t and "/* ---- 顶栏" not in t:
        return t
    m = RE_STICKY_TO_CONTAINER.search(t)
    if not m:
        return t
    new_block = CANON_STICKY_HERO_QUICKNAV.strip() + "\n\n/* ---- Container ---- */"
    return t[: m.start()] + new_block + t[m.end() :]


def _ensure_issue_dock_root_vars(t: str) -> str:
    if "--issue-dock-row-h" in t:
        return t
    if ":root" not in t or "--ix:" not in t:
        return t
    return t.replace(
        "  --ix: 0.18s ease;\n",
        "  --ix: 0.18s ease;\n  --issue-dock-row-h: 52px;\n  --issue-dock-navonly-h: 48px;\n",
        1,
    )


def _ensure_viewport_fit_cover(t: str) -> str:
    if "viewport-fit=cover" in t:
        return t
    old = 'content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"'
    if old not in t:
        return t
    return t.replace(
        old,
        'content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover"',
        1,
    )


def _ensure_fixed_dock_html_classes(t: str) -> str:
    if "detail-issue-top--fixed-dock" in t:
        return t
    if "detail-issue-top" not in t or "issue-sticky-dock" not in t:
        return t
    if "issue-sticky-dock--nav-only" in t and "detail-topbar-inner--with-quicknav" not in t:
        return t.replace(
            '<div class="detail-issue-top">',
            '<div class="detail-issue-top detail-issue-top--fixed-dock detail-issue-top--nav-only-bar">',
            1,
        )
    return t.replace(
        '<div class="detail-issue-top">',
        '<div class="detail-issue-top detail-issue-top--fixed-dock">',
        1,
    )


def _ensure_ix_var_and_tap(t: str) -> str:
    if "var(--ix)" not in t:
        return t
    if ":root" in t[:5000] and "0.18s ease" in t:
        return t
    old = "* { margin: 0; padding: 0; box-sizing: border-box; }"
    if old in t and ":root { --ix:" not in t:
        t = t.replace(
            old,
            old + "\n:root { --ix: 0.18s ease; }\n"
            + "@media (hover: hover) and (pointer: fine) {\n"
            + "  a, button, .atlas-btn, [role=\"button\"] { -webkit-tap-highlight-color: transparent; }\n"
            + "}\n",
            1,
        )
    return t


def _patch_page(html: str) -> tuple[str, bool]:
    t = html
    orig = html

    t = _fix_hero_double_close(t)
    t = _migrate_topbar_html(t)
    t = _reorder_hero_sticky_top(t)
    t = _upgrade_leading_to_dual_sticky(t)
    t = _merge_dual_sticky_to_issue_dock(t)
    t = _collapse_topbar_to_single_row(t)
    t = _nav_only_sub_to_wrapped_topbar(t)
    t = _upgrade_sticky_class_aliases(t)
    t = _inject_hero_tagline(t)
    t = _replace_sticky_hero_quicksnav_css(t)
    t = _ensure_issue_dock_root_vars(t)
    t = _ensure_viewport_fit_cover(t)
    t = _ensure_fixed_dock_html_classes(t)
    t = _ensure_ix_var_and_tap(t)
    t = _patch_i18n_hero_tagline(t)

    t = t.replace("padding: 48px 24px 44px;", "padding: 20px 24px 16px;")
    t = t.replace("padding: 48px 24px 36px;", "padding: 20px 24px 16px;")

    n_total = _extract_total_from_stats(t)
    n_new = t.count("hero-item-count")
    n_old = t.find('<div class="stats">') >= 0
    m_p0 = re.search(r"<p class=\"date\">[\s\S]*?</p>", t, re.MULTILINE)
    if n_old and n_new == 0 and m_p0 and n_total is not None:
        date_s = _date_from_hero_p(m_p0.group(0))
        if date_s:
            t = RE_STATS_INNER.sub("\n", t, count=1)
            new_p = (
                f'  <p class="date">\n'
                f"    {date_s}"
                f'<span class="hero-sep" aria-hidden="true">·</span> '
                f'<span class="hero-count" id="hero-item-count" data-total-items="{n_total}">{n_total}</span>'
                f'<span class="hero-count-unit" data-i18n="hero_count_unit">条</span>\n'
                f"  </p>"
            )
            t = re.sub(
                r"<p class=\"date\">[\s\S]*?</p>",
                new_p,
                t,
                count=1,
                flags=re.MULTILINE,
            )
            t = _patch_i18n_hero(t)

    if ".hero .stats {" in t:
        t2 = RE_OLD_HERO_STATS_CSS.sub("", t, count=1)
        if t2 == t and SPLIT_MARKER in t:
            st = t.find(".hero .stats {")
            if st >= 0:
                en = t.find(SPLIT_MARKER, st)
                if en >= 0:
                    t2 = t[:st] + t[en:]
        t = t2

    t = t.replace("AI Agent 日报", "LavaAgent 今日刊")
    t = t.replace("hero_title: 'AI Agent Daily'", "hero_title: 'LavaAgent · Today'")
    t = _patch_i18n_hero(t)
    t = re.sub(
        r"([0-9]{4}-[0-9]{2}-[0-9]{2})(<span class=\"hero-sep)",
        r"\1 \2",
        t,
    )
    return t, t != orig


def main() -> int:
    paths: list[Path] = [TODAY, *sorted(ARCHIVES.glob("*.html"))]
    n_ok = 0
    n_skip = 0
    for p in paths:
        if not p.is_file():
            print(f"skip (missing): {p}", file=sys.stderr)
            n_skip += 1
            continue
        raw = p.read_text(encoding="utf-8")
        new, did = _patch_page(raw)
        if did:
            p.write_text(new, encoding="utf-8")
            print(f"updated: {p.relative_to(BASE)}")
            n_ok += 1
        else:
            print(f"ok (no change): {p.relative_to(BASE)}")
    print(f"Done. Updated {n_ok} file(s), skipped {n_skip}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
