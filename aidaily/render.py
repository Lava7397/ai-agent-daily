"""HTML/CSS/JS rendering for daily issue and issues archive pages.

Inline assets are loaded from assets/render/ at build time and embedded in the
output HTML (single-file pages; no extra static routes).
"""

from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from html import escape
from pathlib import Path

from aidaily.config import BEIJING_TZ, SITE_URL, TODAY_FILENAME
from aidaily.constants import SECTION_KEYS, SECTION_META
from aidaily.data import get_issue_date, make_item_share_href

_RENDER_ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "render"


@lru_cache(maxsize=None)
def _render_asset(name: str) -> str:
    p = _RENDER_ASSET_DIR / name
    if not p.is_file():
        raise FileNotFoundError(f"Missing render asset: {p}")
    return p.read_text(encoding="utf-8")


def build_item_html(
    item,
    is_top=False,
    *,
    date_str: str,
    section_key: str,
    item_index: int,
):
    safe_title = escape(item.get("title", "Untitled"))
    summary_zh_raw = item.get("summary_zh") or item.get("summary") or ""
    summary_en_raw = item.get("summary_en") or item.get("summary") or summary_zh_raw
    safe_summary_zh = escape(summary_zh_raw)
    safe_summary_en = escape(summary_en_raw)
    safe_link = escape(item.get("url", "#"), quote=True)
    safe_share_href = escape(
        make_item_share_href(date_str, section_key, item_index), quote=True
    )
    top_class = " top" if is_top else ""
    top_badge = '<span class="top-badge">TOP</span>' if is_top else ""
    tags = ""
    if item.get("tags"):
        inner = " ".join(
            f'<span class="tag">{escape(str(t))}</span>' for t in item["tags"]
        )
        tags = f'<div class="card-tags">{inner}</div>'
    return f"""
    <div class="card{top_class}">
      {top_badge}
      <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="card-title">{safe_title}</a>
      <p class="card-summary" data-i18n-text="zh">{safe_summary_zh}</p>
      <p class="card-summary" data-i18n-text="en" hidden>{safe_summary_en}</p>
      <div class="card-actions">
        <div class="card-actions-left">
          <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="read-more" data-i18n="card_read_more">查看原文</a>
          {tags}
        </div>
        <a href="{safe_share_href}" class="card-share" target="_blank" rel="noopener noreferrer" data-i18n="card_share" title="本期推荐·分享" aria-label="分享本条">
          <svg class="card-share-ico" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
          分享
        </a>
      </div>
    </div>"""


def build_section_html(key, items, date_str: str):
    meta = SECTION_META[key]
    section_id = f"section-{key}"
    cards_list = []
    for i, item in enumerate(items):
        cards_list.append(
            build_item_html(
                item,
                is_top=(i == 0),
                date_str=date_str,
                section_key=key,
                item_index=i,
            )
        )
    cards = "\n".join(cards_list)
    return f"""
    <section class="section" id="{section_id}">
      <h2 class="section-title">{meta['icon']} <span data-i18n-text="zh">{meta['title_zh']}</span><span data-i18n-text="en" hidden>{meta['title_en']}</span></h2>
      {cards}
    </section>"""


def build_html(data, include_nav_back=True):
    date_str = get_issue_date(data)
    safe_date = escape(date_str)
    total = sum(len(data.get(k, [])) for k in SECTION_KEYS)
    blurb = (data.get("description") or "").strip()
    if not blurb:
        blurb = "AI Agent 领域最新研究、GitHub 热门项目、模型大厂动态"
    safe_blurb = escape(blurb, quote=True)
    sources_raw = (data.get("sources") or "").strip()
    safe_sources_attr = escape(sources_raw, quote=True) if sources_raw else ""
    meta_desc = f"今日刊 {safe_date} — {safe_blurb}"
    if safe_sources_attr:
        meta_desc = f"{meta_desc} · 来源：{safe_sources_attr}"
    og_desc = f"今日 {total} 条精选 · {safe_blurb}"
    if safe_sources_attr:
        og_desc = f"{og_desc} · {safe_sources_attr}"
    hero_sources_html = (
        f'\n  <p class="hero-sources">{escape(sources_raw)}</p>' if sources_raw else ""
    )
    sections = []
    for key in SECTION_KEYS:
        items = data.get(key, [])
        if items:
            sections.append(build_section_html(key, items, date_str))
    sections_html = "\n".join(sections)
    nav_items = [
        ("research", "AI Agent 研究"),
        ("github", "GitHub 热门"),
        ("models", "模型动态"),
        ("community", "社区热议"),
    ]
    quick_nav_html = "".join(
        f'<a class="quick-link" href="#section-{k}">{escape(v)}</a>' for k, v in nav_items if data.get(k, [])
    )

    back_block = (
        """<a href="home.html" class="atlas-btn" id="back-home" aria-label="返回首页"><span aria-hidden="true">←</span> <span data-i18n="nav_back_text">返回</span></a>"""
        if include_nav_back
        else ""
    )
    lang_block = (
        """<div class="atlas-lang" role="group" aria-label="界面语言">
      <button type="button" id="lang-zh" data-set-lang="zh">中</button>
      <span class="atlas-lang-sep">/</span>
      <button type="button" id="lang-en" data-set-lang="en">EN</button>
    </div>"""
        if include_nav_back
        else ""
    )
    quick_nav_block = f"""<nav class="quick-nav quick-nav--inline" aria-label="内容导航">
  {quick_nav_html}
</nav>"""
    nav_row_nav_only = f"""<div class="detail-topbar">
  <div class="detail-topbar-inner detail-topbar-inner--nav-only">
<nav class="quick-nav" aria-label="内容导航">
  {quick_nav_html}
</nav>
  </div>
</div>"""
    # 单块 sticky：返回、四格、语言同在一行，Hero 在下方
    hero_block = f"""<div class="hero">
  <h1 data-i18n="hero_title">今日刊</h1>
  <p class="date">
    {safe_date} <span class="hero-sep" aria-hidden="true">·</span> <span class="hero-tagline" data-i18n="hero_tagline">每日精选</span> <span class="hero-sep" aria-hidden="true">·</span> <span class="hero-count" id="hero-item-count" data-total-items="{total}">{total}</span><span class="hero-count-unit" data-i18n="hero_count_unit">条</span>
  </p>{hero_sources_html}
</div>
"""
    if include_nav_back:
        issue_top = f"""<div class="detail-issue-top detail-issue-top--fixed-dock">
<header class="issue-sticky-dock" aria-label="日刊顶栏与栏目导航">
<div class="detail-topbar">
  <div class="detail-topbar-inner detail-topbar-inner--with-quicknav">
{back_block}
{quick_nav_block}
{lang_block}
  </div>
</div>
</header>
{hero_block}
</div>"""
    else:
        issue_top = f"""<div class="detail-issue-top detail-issue-top--fixed-dock detail-issue-top--nav-only-bar">
{hero_block}
<header class="issue-sticky-dock issue-sticky-dock--nav-only" aria-label="栏目导航">
{nav_row_nav_only}
</header>
</div>"""
    back_home_js = (
        "(function(){var el=document.getElementById('back-home');if(!el)return;"
        "var p=location.pathname||'';if(p.indexOf('/archives/')!==-1)"
        "el.setAttribute('href','../home.html');})();\n\n"
        if include_nav_back
        else ""
    )

    issue_css = _render_asset("daily-issue.css")
    issue_i18n_js = _render_asset("daily-issue-i18n.js")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="description" content="{meta_desc}">
<meta name="theme-color" content="#0d1b2a">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:title" content="今日刊 — {safe_date}">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE_URL}">
<meta name="twitter:card" content="summary">
<title>今日刊 — {safe_date}</title>
<style>
{issue_css}
</style>
</head>
<body>
<a href="#main-content" class="skip-link" data-i18n="skip_to_content">跳到正文</a>
{issue_top}
<!-- Content -->
<main class="container" id="main-content">
  {sections_html}
</main>

<script>
{back_home_js}{issue_i18n_js}
</script>

</body>
</html>"""



def build_issues_html(archive_infos, page=1, per_page=10):
    """生成 issues.html：AI Agent 期刊历史归档列表（分页），独立页面。

    archive_infos: list of (date_str, headline, total_items, summary)
    """
    total = len(archive_infos)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    page_infos = archive_infos[start:end]
    latest_issue_href = TODAY_FILENAME

    # 生成日期卡片（含头条摘要）
    cards_html = ""
    for date_str, headline, items_total, summary in page_infos:
        day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][
            datetime.strptime(date_str, "%Y-%m-%d").weekday()
        ]
        safe_headline = escape(headline) if headline else "暂无摘要"
        safe_summary = escape(summary) if summary else ""
        summary_html = (
            f'<p class="date-summary">{safe_summary}</p>' if safe_summary else ""
        )
        try:
            n_total = int(str(items_total).strip()) if items_total not in (None, "") else 0
        except ValueError:
            n_total = 0
        if n_total > 0:
            right_col = f"""<span class="date-arrow-stack" aria-label="{n_total} 条内容" title="{n_total} 条内容">
              <span class="date-count-num">{n_total}</span>
              <span class="date-arrow" aria-hidden="true">→</span>
            </span>"""
        else:
            right_col = '<span class="date-arrow-stack date-arrow-stack--empty" aria-hidden="true"><span class="date-arrow">→</span></span>'
        cards_html += f"""
        <a class="date-card" href="archives/{date_str}.html">
          <div class="date-meta-wrap">
            <span class="date-main">{date_str}</span>
            <span class="date-day">{day_name}</span>
          </div>
          <div class="date-text-wrap">
            <p class="date-headline">{safe_headline}</p>
            {summary_html}
          </div>
          <div class="date-right">
            {right_col}
          </div>
        </a>"""

    # 生成分页导航
    page_btns = ""
    for p in range(1, total_pages + 1):
        active = " active" if p == page else ""
        page_btns += f'<button class="page-btn{active}" data-page="{p}">{p}</button>'

    prev_btn = f'<button class="page-btn nav-btn" data-page="{page-1}" {"disabled" if page <= 1 else ""}>‹ 上一页</button>' if page > 1 else '<button class="page-btn nav-btn" disabled>‹ 上一页</button>'
    next_btn = f'<button class="page-btn nav-btn" data-page="{page+1}" {"disabled" if page >= total_pages else ""}>下一页 ›</button>' if page < total_pages else '<button class="page-btn nav-btn" disabled>下一页 ›</button>'

    generated_at = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
    # JSON 序列化，供 JS 端分页使用
    all_archives_json = json.dumps(archive_infos, ensure_ascii=False)

    issues_css = _render_asset("issues-archive.css")
    issues_js = (
        _render_asset("issues-archive.js")
        .replace("__ALL_ARCHIVES_JSON__", all_archives_json)
        .replace("__PER_PAGE__", str(int(per_page)))
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="description" content="AI Agent 期刊 · 历史归档 — 共 {total} 期">
<meta name="theme-color" content="#0d1b2a">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<title>AI Agent 期刊 · 历史归档</title>
<style>
{issues_css}
</style>
</head>
<body>
<a href="#main-content" class="skip-link">跳到正文</a>
<div class="detail-issue-top detail-issue-top--fixed-dock">
<header class="issue-sticky-dock" aria-label="期刊归档顶栏">
<div class="detail-topbar">
  <div class="detail-topbar-inner detail-topbar-inner--with-quicknav">
<a href="home.html" class="atlas-btn" id="back-home" aria-label="返回首页"><span aria-hidden="true">←</span> <span>返回</span></a>
  </div>
</div>
</header>

<!-- Hero -->
<div class="hero">
  <h1>AI Agent 期刊</h1>
  <p class="subtitle">历史存档 · 共 {total} 期</p>
  <a class="today-link" href="{latest_issue_href}">查看今日刊 →</a>
</div>

</div>
<main id="main-content">

<!-- Stats -->
<div class="stats-bar">
  <div class="stat">
    <div class="stat-num">{total}</div>
    <div class="stat-label">Total Issues</div>
  </div>
  <div class="stat">
    <div class="stat-num">{total_pages}</div>
    <div class="stat-label">Pages</div>
  </div>
  <div class="stat">
    <div class="stat-num">{per_page}</div>
    <div class="stat-label">Per Page</div>
  </div>
</div>

<!-- Archive list -->
<div class="archive-wrap">
  <div class="archive-list" id="archiveList">
    {cards_html}
  </div>

  <!-- Pagination -->
  <div class="pagination" id="pagination">
    {prev_btn}
    {page_btns}
    {next_btn}
    <span class="page-info">第 {page} / {total_pages} 页</span>
  </div>
</div>

</main>
<!-- Footer -->
<div class="footer">
  <p>Generated at {generated_at} · Powered by Lava Agent</p>
  <p style="margin-top:6px;"><a href="home.html">首页</a> · <a href="{latest_issue_href}">今日刊</a></p>
</div>

<script>
{issues_js}
</script>
</body>
</html>"""
