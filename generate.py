#!/usr/bin/env python3
"""
AI Agent 日报 H5 页面生成器
读取 daily_data.json → 生成 today.html(当天刊) + 归档页面
"""
import argparse
import json
import os
import re
import sys
from html import escape
from datetime import datetime, timezone, timedelta
from pathlib import Path

BEIJING_TZ = timezone(timedelta(hours=8))

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "daily_data.json"
OUTPUT_DIR = BASE_DIR / "archives"

# 当天刊文件名。不能用 index.html: 静态托管会把 URL `/` 映射到根目录的
# index.html,优先于 vercel.json 里把 `/` 重写到 home.html,导致首页变成「当天刊」。
TODAY_FILENAME = "today.html"

# Canonical public URL for the site. Override with SITE_URL env var if needed.
# Keep in sync with CNAME file and Vercel custom domain settings.
SITE_URL = os.environ.get("SITE_URL", "https://lava7397.com")


def current_beijing_date_str():
    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")


def get_issue_date(data):
    return str(data.get("date") or current_beijing_date_str())


def sync_today_html_from_newest_archive():
    """将 today.html 写成「archives/ 下日期 YYYY-MM-DD 最大」的那一期。

    与 home 页把「今日刊」指向「列表第一条（最新期）」的语义一致；也修复
    daily_data 里 date 未跟上时，/today.html 内容落后于 archives 的问题。
    """
    paths = sorted(OUTPUT_DIR.glob("????-??-??.html"), key=lambda p: p.stem)
    if not paths:
        return
    latest = paths[-1]
    today_path = BASE_DIR / TODAY_FILENAME
    today_path.write_text(latest.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Synced {TODAY_FILENAME} ← {latest.name} (newest archive)")


def replace_between(text, start_marker, end_marker, replacement):
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"start marker not found: {start_marker}")
    end = text.find(end_marker, start + len(start_marker))
    if end == -1:
        raise ValueError(f"end marker not found: {end_marker}")
    return text[: start + len(start_marker)] + replacement + text[end:]


def extract_between(text, start_marker, end_marker):
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"start marker not found: {start_marker}")
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"end marker not found: {end_marker}")
    return text[start:end]


def extract_archive_meta(archive_path):
    """从归档 HTML 中提取头条标题和总条目数"""
    try:
        html = archive_path.read_text(encoding="utf-8")
        # 提取第一个 .card-title 的文本（头条标题）
        m = re.search(r'<a[^>]+class="card-title"[^>]*>([^<]+)</a>', html)
        headline = m.group(1).strip() if m else ""
        # 提取总条目数（hero stats 里）
        n = re.findall(r'class="stat-num"[^>]*>([\d]+)</div>', html)
        total = n[0] if n else ""   # 第一个 stat-num 是 total items
        return headline, total
    except Exception:
        return "", ""


def build_home_html(archive_infos, page=1, per_page=10):
    """生成首页 home.html：展示所有历史归档，支持分页
    archive_infos: list of (date_str, headline, total_items)
    """

SECTION_META = {
    "research": {"icon": "🤖", "title": "AI Agent 研究"},
    "github":   {"icon": "⭐", "title": "GitHub 热门项目"},
    "models":   {"icon": "🚀", "title": "模型与行业动态"},
    "community": {"icon": "🔥", "title": "社区热议"},
}


def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def build_item_html(item, is_top=False):
    safe_title = escape(item.get("title", "Untitled"))
    safe_summary = escape(item.get("summary", ""))
    safe_link = escape(item.get("url", "#"), quote=True)
    top_class = " top" if is_top else ""
    top_badge = '<span class="top-badge">TOP</span>' if is_top else ""
    tags = ""
    if item.get("tags"):
        tags = " ".join(
            f'<span class="tag">{escape(str(t))}</span>' for t in item["tags"]
        )
    return f"""
    <div class="card{top_class}">
      {top_badge}
      <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="card-title">{safe_title}</a>
      <p class="card-summary">{safe_summary}</p>
      <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="read-more">查看原文</a>
      {tags}
    </div>"""


def build_section_html(key, items):
    meta = SECTION_META[key]
    section_id = f"section-{key}"
    cards_list = []
    for i, item in enumerate(items):
        cards_list.append(build_item_html(item, is_top=(i == 0)))
    cards = "\n".join(cards_list)
    return f"""
    <section class="section" id="{section_id}">
      <h2 class="section-title">{meta['icon']} {meta['title']}</h2>
      {cards}
    </section>"""


def build_html(data, include_nav_back=True):
    date_str = get_issue_date(data)
    safe_date = escape(date_str)
    sections = []
    for key in ("research", "github", "models", "community"):
        items = data.get(key, [])
        if items:
            sections.append(build_section_html(key, items))
    sections_html = "\n".join(sections)

    # Count total items
    total = sum(len(data.get(k, [])) for k in ("research", "github", "models", "community"))
    sources = data.get("sources", "arXiv, GitHub, Anthropic, Google, TechCrunch")
    source_list = [s.strip() for s in sources.split(",") if s.strip()]
    safe_sources = escape(sources)
    source_count = len(source_list)
    section_count = sum(1 for k in ("research", "github", "models", "community") if data.get(k, []))
    generated_at = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
    safe_generated_at = escape(generated_at)
    nav_items = [
        ("research", "AI Agent 研究"),
        ("github", "GitHub 热门"),
        ("models", "模型动态"),
        ("community", "社区热议"),
    ]
    quick_nav_html = "".join(
        f'<a class="quick-link" href="#section-{k}">{escape(v)}</a>' for k, v in nav_items if data.get(k, [])
    )

    detail_topbar_block = ""
    if include_nav_back:
        detail_topbar_block = """<div class="detail-topbar">
  <div class="detail-topbar-inner">
    <a href="home.html" class="atlas-btn" id="back-home" aria-label="返回 LavaAgent 首页"><span aria-hidden="true">←</span> 返回</a>
  </div>
</div>
"""
    back_home_js = (
        "(function(){var el=document.getElementById('back-home');if(!el)return;"
        "var p=location.pathname||'';if(p.indexOf('/archives/')!==-1)"
        "el.setAttribute('href','../home.html');})();\n\n"
        if include_nav_back
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="description" content="AI Agent 日报 {safe_date} — AI Agent 领域最新研究、GitHub 热门项目、模型大厂动态">
<meta name="theme-color" content="#0d1b2a">
<meta property="og:title" content="AI Agent 日报 — {safe_date}">
<meta property="og:description" content="今日 {total} 条 AI 资讯精选：Agent 研究、GitHub 热门、模型大厂动态">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE_URL}">
<meta name="twitter:card" content="summary">
<title>AI Agent 日报 — {safe_date}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f5f0e8;
  color: #2c2c2c;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}}

/* ---- Detail top bar（与 quick-nav / 正文同宽，按钮同首页 atlas-btn） ---- */
.detail-topbar {{
  max-width: 720px;
  margin: 0 auto;
  padding: 20px 16px 0;
}}
.detail-topbar-inner {{
  display: flex;
  justify-content: flex-start;
  align-items: center;
}}
.atlas-btn {{
  border: 1px solid rgba(100,80,60,0.18);
  color: #4d4338;
  background: #f8f4eb;
  text-decoration: none;
  padding: 8px 14px;
  font-size: 11px;
  letter-spacing: 1.1px;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  -webkit-tap-highlight-color: transparent;
}}

/* ---- Hero / 莫比斯封面 ---- */
.hero {{
  background:
    radial-gradient(ellipse at 20% 80%, rgba(178,200,218,0.35) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(210,185,220,0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(245,235,210,0.5) 0%, transparent 70%),
    #f5f0e8;
  padding: 48px 24px 44px;
  text-align: center;
  position: relative;
  border-bottom: 2px solid rgba(100,80,60,0.15);
}}
.hero::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 3px,
    rgba(100,80,60,0.02) 3px, rgba(100,80,60,0.02) 4px
  );
  pointer-events: none;
}}
.hero h1 {{
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 38px;
  font-weight: 700;
  color: #3a3a3a;
  letter-spacing: 3px;
  position: relative;
  z-index: 1;
}}
.hero .date {{
  color: #8a7e6e;
  font-size: 13px;
  margin-top: 10px;
  position: relative;
  z-index: 1;
  letter-spacing: 2px;
}}
.hero .stats {{
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 28px;
  position: relative;
  z-index: 1;
}}
.hero .stat {{
  text-align: center;
  border: 1px solid rgba(100,80,60,0.12);
  padding: 14px 22px;
  background: rgba(255,255,255,0.5);
  backdrop-filter: blur(4px);
}}
.hero .stat-num {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 30px;
  font-weight: 700;
  color: #5a6e8a;
}}
.hero .stat-label {{
  font-size: 10px;
  color: #8a7e6e;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}}

/* ---- Quick Nav ---- */
.quick-nav {{
  max-width: 720px;
  margin: 0 auto;
  padding: 20px 16px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}}
.quick-link {{
  display: inline-block;
  padding: 8px 16px;
  text-decoration: none;
  color: #5a6e8a;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(90,110,138,0.2);
  font-size: 12px;
  font-family: 'Inter', sans-serif;
  letter-spacing: 0.5px;
  transition: all 0.25s;
}}
.quick-link:hover {{
  color: #fff;
  background: #5a6e8a;
  border-color: #5a6e8a;
}}

/* ---- Container ---- */
.container {{
  max-width: 720px;
  margin: 0 auto;
  padding: 0 16px 100px;
}}

/* ---- Section ---- */
.section {{
  margin-top: 44px;
}}
.section-title {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 20px;
  font-weight: 700;
  color: #4a6080;
  padding: 12px 0;
  margin-bottom: 24px;
  border-bottom: 2px solid rgba(90,110,138,0.25);
  letter-spacing: 1px;
}}

/* ---- Card / 莫比斯分格 ---- */
.card {{
  background: rgba(255,255,255,0.65);
  border: 1px solid rgba(100,80,60,0.15);
  border-left: 3px solid #9ab8d0;
  padding: 26px;
  margin-bottom: 24px;
  transition: all 0.25s;
  position: relative;
}}
.card::before {{
  content: '';
  position: absolute;
  left: -3px;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #b2c8da, #d2b9dc);
  opacity: 0;
  transition: opacity 0.25s;
}}
.card:hover {{
  border-left-color: transparent;
  background: rgba(255,255,255,0.85);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(100,80,60,0.08);
}}
.card:hover::before {{
  opacity: 1;
}}

/* ---- TOP card 高标 ---- */
.card.top {{
  background: rgba(255,255,255,0.85);
  border-left: 3px solid #4a6080;
  border-color: rgba(74,96,128,0.25);
  padding: 28px 26px 26px;
}}
.card.top .card-title {{
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
}}
.card.top .card-summary {{
  color: #3a3a3a;
}}
.top-badge {{
  display: inline-block;
  font-size: 9px;
  font-weight: 600;
  color: #fff;
  background: #4a6080;
  padding: 2px 8px;
  margin-bottom: 10px;
  letter-spacing: 1.5px;
}}
.card-title {{
  font-family: 'Cormorant Garamond', serif;
  color: #1a1a1a;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.5;
  text-decoration: none;
  display: block;
}}
.card-title:hover {{
  color: #5a6e8a;
}}
.card-summary {{
  color: #4a4a4a;
  font-size: 14px;
  line-height: 1.9;
  margin-top: 14px;
  border-top: 1px solid rgba(100,80,60,0.08);
  padding-top: 14px;
}}
.read-more {{
  display: inline-block;
  margin-top: 14px;
  font-size: 12px;
  color: #5a6e8a;
  text-decoration: none;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(90,110,138,0.3);
  padding-bottom: 2px;
  transition: all 0.2s;
}}
.read-more:hover {{
  border-bottom-color: #5a6e8a;
}}
.tag {{
  display: inline-block;
  background: rgba(154,184,208,0.2);
  color: #4a6080;
  font-size: 11px;
  padding: 4px 10px;
  margin-top: 14px;
  margin-right: 6px;
  border: 1px solid rgba(90,110,138,0.12);
  font-family: 'Inter', sans-serif;
  letter-spacing: 0.5px;
}}

/* ---- Share Bar ---- */
.share-bar {{
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(245,240,232,0.97);
  backdrop-filter: blur(8px);
  border-top: 1px solid rgba(100,80,60,0.1);
  padding: 14px 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
  z-index: 100;
}}
.share-btn {{
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid rgba(100,80,60,0.15);
  color: #5a5a5a;
  padding: 10px 18px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
  -webkit-tap-highlight-color: transparent;
}}
.share-btn:hover {{
  border-color: #5a6e8a;
  color: #5a6e8a;
}}
.share-btn.primary {{
  background: #5a6e8a;
  border-color: #5a6e8a;
  color: #fff;
}}
.share-btn.primary:hover {{
  background: #4a5e7a;
}}
.share-btn .icon {{ font-size: 15px; }}

.skip-link {{
  position: absolute;
  top: -40px;
  left: 0;
  background: #5a6e8a;
  color: #fff;
  padding: 8px 16px;
  z-index: 1000;
}}
.skip-link:focus {{ top: 0; }}

/* ---- Footer ---- */
.footer {{
  max-width: 720px;
  margin: 0 auto;
  padding: 24px 16px;
  text-align: center;
  color: #aaa090;
  font-size: 11px;
  border-top: 1px solid rgba(100,80,60,0.08);
  letter-spacing: 0.5px;
}}

/* ---- Toast ---- */
.toast {{
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%) translateY(20px);
  background: #5a6e8a;
  color: #fff;
  padding: 12px 24px;
  font-size: 13px;
  font-weight: 500;
  opacity: 0;
  transition: all 0.3s;
  z-index: 200;
}}
.toast.show {{
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}}

/* ---- Modal ---- */
.modal-overlay {{
  position: fixed;
  inset: 0;
  background: rgba(245,240,232,0.92);
  display: none;
  justify-content: center;
  align-items: center;
  z-index: 300;
}}
.modal-overlay.show {{ display: flex; }}
.modal {{
  background: #fff;
  border: 1px solid rgba(100,80,60,0.1);
  padding: 32px;
  max-width: 320px;
  width: 90%;
  text-align: center;
  box-shadow: 0 16px 48px rgba(0,0,0,0.08);
}}
.modal h3 {{
  font-family: 'Cormorant Garamond', serif;
  color: #5a6e8a;
  margin-bottom: 20px;
  letter-spacing: 1px;
}}
.qr-placeholder {{
  width: 200px;
  height: 200px;
  margin: 0 auto 20px;
  background: rgba(178,200,218,0.1);
  border: 1px dashed rgba(90,110,138,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  font-size: 12px;
}}
.qr-placeholder img {{ max-width: 100%; }}
.close-btn {{
  background: transparent;
  border: 1px solid rgba(100,80,60,0.15);
  color: #5a6e8a;
  padding: 10px 24px;
  cursor: pointer;
  transition: all 0.2s;
}}
.close-btn:hover {{
  background: #5a6e8a;
  color: #fff;
}}
</style>
</head>
<body>
<a href="#main-content" class="skip-link">跳到正文</a>
{detail_topbar_block}
<!-- Hero -->
<div class="hero">
  <h1>AI Agent 日报</h1>
  <p class="date">{safe_date} · 每日精选</p>
  <div class="stats">
    <div class="stat">
      <div class="stat-num">{total}</div>
      <div class="stat-label">条资讯</div>
    </div>
    <div class="stat">
      <div class="stat-num">{section_count}</div>
      <div class="stat-label">个板块</div>
    </div>
    <div class="stat">
      <div class="stat-num">{source_count}</div>
      <div class="stat-label">个来源</div>
    </div>
  </div>
</div>

<nav class="quick-nav" aria-label="内容导航">
  {quick_nav_html}
</nav>

<!-- Content -->
<main class="container" id="main-content">
  {sections_html}
</main>

<!-- Footer -->
<div class="footer">
  数据来源：{safe_sources}<br>
  由 Hermes Agent 自动生成 · 每日北京时间 11:30 更新 · 生成时间 {safe_generated_at}
</div>

<!-- Share Bar -->
<div class="share-bar">
  <button class="share-btn primary" onclick="downloadImage()">
    <span class="icon">📸</span> 保存图片
  </button>
  <button class="share-btn" onclick="shareWechat()">
    <span class="icon">💬</span> 微信分享
  </button>
  <button class="share-btn" onclick="copyLink()">
    <span class="icon">🔗</span> 复制链接
  </button>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<!-- WeChat Modal -->
<div class="modal-overlay" id="wechatModal" onclick="closeModal(event)">
  <div class="modal">
    <h3>📱 微信扫码分享</h3>
    <div class="qr-placeholder" id="qrCode">
      部署后自动生成二维码
    </div>
    <p style="color:#666;font-size:12px;margin-bottom:16px;">截图或长按保存，发送给朋友</p>
    <button class="close-btn" onclick="document.getElementById('wechatModal').classList.remove('show')">关闭</button>
  </div>
</div>

<script>
{back_home_js}const SHARE_URL = '{SITE_URL}';

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1800);
}}

function copyLink() {{
  const url = SHARE_URL;
  if (navigator.clipboard) {{
    navigator.clipboard.writeText(url).then(() => showToast('✅ 链接已复制'));
  }} else {{
    const ta = document.createElement('textarea');
    ta.value = url;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('✅ 链接已复制');
  }}
}}

function shareWechat() {{
  const modal = document.getElementById('wechatModal');
  const qrCode = document.getElementById('qrCode');
  const qrApi = 'https://api.qrserver.com/v1/create-qr-code/?size=360x360&data=' + encodeURIComponent(SHARE_URL);

  qrCode.innerHTML = '<img alt="微信分享二维码" src="' + qrApi + '" />';
  const qrImg = qrCode.querySelector('img');
  if (qrImg) {{
    qrImg.onerror = () => {{
      qrCode.textContent = '二维码加载失败，请使用“复制链接”分享';
    }};
  }}

  modal.classList.add('show');
}}

function closeModal(e) {{
  if (e.target === e.currentTarget) {{
    e.currentTarget.classList.remove('show');
  }}
}}

function downloadImage() {{
  const date = '{safe_date}';
  const fileName = `AI-Agent日报-${{date}}.png`;
  const shareBar = document.querySelector('.share-bar');
  const toast = document.getElementById('toast');

  showToast('📸 正在生成图片…');
  if (shareBar) shareBar.style.display = 'none';
  if (toast) toast.style.display = 'none';

  const body = document.body;
  const origWidth = body.style.width;
  body.style.width = '720px';

  html2canvas(body, {{
    scale: 2,
    useCORS: true,
    backgroundColor: '#f5f0e8',
    width: 720,
    windowWidth: 720
  }}).then(canvas => {{
    body.style.width = origWidth;
    if (shareBar) shareBar.style.display = '';
    if (toast) toast.style.display = '';
    canvas.toBlob(blob => {{
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast('✅ 图片已保存');
    }}, 'image/png');
  }}).catch(err => {{
    body.style.width = origWidth;
    if (shareBar) shareBar.style.display = '';
    if (toast) toast.style.display = '';
    showToast('❌ 截图失败: ' + err.message);
  }});
}}
</script>

</body>
</html>"""



def build_home_html(archive_infos, page=1, per_page=10):
    """生成首页 home.html：展示所有历史归档，支持分页
    archive_infos: list of (date_str, headline, total_items)
    """
    total = len(archive_infos)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    page_infos = archive_infos[start:end]
    latest_issue_href = (
        f"archives/{archive_infos[0][0]}.html" if archive_infos else TODAY_FILENAME
    )

    # 生成日期卡片（含头条摘要）
    cards_html = ""
    for date_str, headline, items_total in page_infos:
        day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][
            datetime.strptime(date_str, "%Y-%m-%d").weekday()
        ]
        safe_headline = escape(headline) if headline else "暂无摘要"
        items_label = f"{items_total} 条内容" if items_total else ""
        cards_html += f"""
        <a class="date-card" href="archives/{date_str}.html">
          <div class="date-meta-wrap">
            <span class="date-main">{date_str}</span>
            <span class="date-day">{day_name}</span>
          </div>
          <p class="date-headline">{safe_headline}</p>
          <div class="date-right">
            {f'<span class="date-count">{items_label}</span>' if items_label else ''}
            <span class="date-arrow">→</span>
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

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="description" content="AI Agent 日报 · 历史存档 — 共 {total} 期">
<meta name="theme-color" content="#0d1b2a">
<title>AI Agent 日报 · 历史存档</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f5f0e8;
  color: #2c2c2c;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}}

/* ---- Hero ---- */
.hero {{
  background:
    radial-gradient(ellipse at 20% 80%, rgba(178,200,218,0.35) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(210,185,220,0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(245,235,210,0.5) 0%, transparent 70%),
    #f5f0e8;
  padding: 52px 24px 40px;
  text-align: center;
  position: relative;
  border-bottom: 2px solid rgba(100,80,60,0.15);
}}
.hero::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 3px,
    rgba(100,80,60,0.02) 3px, rgba(100,80,60,0.02) 4px
  );
  pointer-events: none;
}}
.hero h1 {{
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 34px;
  font-weight: 700;
  color: #3a3a3a;
  letter-spacing: 3px;
  position: relative;
  z-index: 1;
}}
.hero .subtitle {{
  color: #8a7e6e;
  font-size: 13px;
  margin-top: 10px;
  position: relative;
  z-index: 1;
  letter-spacing: 1.5px;
}}
.hero .today-link {{
  display: inline-block;
  margin-top: 24px;
  padding: 10px 22px;
  background: #5a6e8a;
  color: #fff;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 1px;
  border-radius: 4px;
  position: relative;
  z-index: 1;
  transition: background 0.2s;
}}
.hero .today-link:hover {{ background: #4a6080; }}

/* ---- Stats bar ---- */
.stats-bar {{
  max-width: 720px;
  margin: 28px auto 0;
  padding: 0 24px;
  display: flex;
  justify-content: center;
  gap: 32px;
}}
.stats-bar .stat {{
  text-align: center;
  border: 1px solid rgba(100,80,60,0.12);
  padding: 12px 20px;
  background: rgba(255,255,255,0.5);
}}
.stats-bar .stat-num {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 26px;
  font-weight: 700;
  color: #5a6e8a;
}}
.stats-bar .stat-label {{
  font-size: 10px;
  color: #8a7e6e;
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}}

/* ---- Archive list ---- */
.archive-wrap {{
  max-width: 720px;
  margin: 0 auto;
  padding: 32px 20px 60px;
}}
.archive-list {{
  display: flex;
  flex-direction: column;
  gap: 10px;
}}
.date-card {{
  display: flex;
  align-items: center;
  gap: 10px 12px;
  padding: 14px 18px;
  background: rgba(255,255,255,0.65);
  border: 1px solid rgba(100,80,60,0.1);
  border-left: 4px solid #5a6e8a;
  text-decoration: none;
  color: #2c2c2c;
  border-radius: 2px;
  transition: all 0.18s ease;
}}
.date-card:nth-child(5n+2) {{ border-left-color: #7a6e9a; }}
.date-card:nth-child(5n+3) {{ border-left-color: #6a8a7a; }}
.date-card:nth-child(5n+4) {{ border-left-color: #8a7a6a; }}
.date-card:nth-child(5n+5) {{ border-left-color: #6a7a8a; }}
.date-card:hover {{
  background: rgba(255,255,255,0.9);
  border-left-color: #4a6080;
  transform: translateX(4px);
}}
.date-meta-wrap {{
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}}
.date-main {{
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 17px;
  font-weight: 600;
  color: #3a3a3a;
  white-space: nowrap;
}}
.date-day {{
  font-size: 11px;
  color: #8a7e6e;
  letter-spacing: 1px;
}}
.date-headline {{
  flex: 1;
  font-size: 13px;
  color: #5a5040;
  line-height: 1.5;
  margin: 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-width: 0;
}}
.date-right {{
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.date-count {{
  font-size: 11px;
  color: #8a7e6e;
  white-space: nowrap;
}}
.date-arrow {{
  font-size: 16px;
  color: #b0a89a;
  transition: transform 0.18s, color 0.18s;
}}
.date-card:hover .date-arrow {{
  transform: translateX(3px);
  color: #5a6e8a;
}}

/* ---- Pagination ---- */
.pagination {{
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 36px;
  flex-wrap: wrap;
}}
.page-btn {{
  padding: 8px 14px;
  border: 1px solid rgba(100,80,60,0.15);
  background: rgba(255,255,255,0.6);
  color: #5a6e8a;
  font-size: 13px;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.15s;
  min-width: 40px;
}}
.page-btn:hover:not(:disabled) {{
  background: #5a6e8a;
  color: #fff;
  border-color: #5a6e8a;
}}
.page-btn.active {{
  background: #4a6080;
  color: #fff;
  border-color: #4a6080;
  font-weight: 600;
}}
.page-btn:disabled {{
  opacity: 0.35;
  cursor: not-allowed;
}}
.page-info {{
  font-size: 12px;
  color: #8a7e6e;
  margin: 0 8px;
  letter-spacing: 1px;
}}

/* ---- Footer ---- */
.footer {{
  text-align: center;
  padding: 32px 20px;
  border-top: 1px solid rgba(100,80,60,0.1);
  color: #a09080;
  font-size: 11px;
  letter-spacing: 1px;
}}
.footer a {{ color: #8a7e6e; text-decoration: none; }}
.footer a:hover {{ color: #5a6e8a; }}
</style>
</head>
<body>

<!-- Hero -->
<div class="hero">
  <h1>AI Agent 日报</h1>
  <p class="subtitle">历史存档 · 共 {total} 期</p>
  <a class="today-link" href="{latest_issue_href}">查看当天日报 →</a>
</div>

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

<!-- Footer -->
<div class="footer">
  <p>Generated at {generated_at} · Powered by Lava Agent</p>
  <p style="margin-top:6px;"><a href="{latest_issue_href}">当天日报</a> · <a href="home.html">历史存档</a></p>
</div>

<script>
// 所有归档数据（按日期降序）: [date_str, headline, total_items]
const ALL_ARCHIVES = {all_archives_json};

const PER_PAGE = {per_page};
const totalPages = Math.max(1, Math.ceil(ALL_ARCHIVES.length / PER_PAGE));

function renderPage(p) {{
  p = Math.max(1, Math.min(p, totalPages));
  const start = (p - 1) * PER_PAGE;
  const end = start + PER_PAGE;
  const pageItems = ALL_ARCHIVES.slice(start, end);

  const dayNames = ['周日','周一','周二','周三','周四','周五','周六'];
  const listEl = document.getElementById('archiveList');
  listEl.innerHTML = pageItems.map(([d, headline, total]) => {{
    const dn = dayNames[new Date(d + 'T00:00:00').getDay()];
    const label = total ? total + ' 条内容' : '';
    const countHtml = label ? `<span class="date-count">${{label}}</span>` : '';
    return `<a class="date-card" href="archives/${{d}}.html">
      <div class="date-meta-wrap">
        <span class="date-main">${{d}}</span>
        <span class="date-day">${{dn}}</span>
      </div>
      <p class="date-headline">${{headline || '暂无摘要'}}</p>
      <div class="date-right">
        ${{countHtml}}
        <span class="date-arrow">→</span>
      </div>
    </a>`;
  }}).join('');

  // 更新分页按钮
  const pager = document.getElementById('pagination');
  const btns = pager.querySelectorAll('.page-btn[data-page]');
  btns.forEach(b => {{
    b.classList.toggle('active', parseInt(b.dataset.page) === p);
    b.disabled = parseInt(b.dataset.page) < 1 || parseInt(b.dataset.page) > totalPages;
  }});

  // 更新 page info
  let info = pager.querySelector('.page-info');
  if (info) info.textContent = `第 ${{p}} / ${{totalPages}} 页`;

  // 更新 URL hash
  history.replaceState(null, '', p > 1 ? `#page=${{p}}` : window.location.pathname);
}}

// 绑定分页按钮点击
document.getElementById('pagination').addEventListener('click', e => {{
  const btn = e.target.closest('.page-btn');
  if (!btn || btn.disabled) return;
  renderPage(parseInt(btn.dataset.page));
}});

// 初始化：读取 hash 或默认第1页
const hash = window.location.hash;
const initPage = hash ? parseInt(hash.replace('#page=', '')) || 1 : 1;
renderPage(initPage);
</script>
</body>
</html>"""


def run_source_evolution():
    print("\n🧬 Running source evolution...")
    try:
        import subprocess
        evo_result = subprocess.run(
            ["python3", str(BASE_DIR / "scripts" / "source_evolution.py")],
            capture_output=True, text=True, timeout=60
        )
        if evo_result.returncode == 0:
            print(evo_result.stdout[-1500:] if len(evo_result.stdout) > 1500 else evo_result.stdout)
        else:
            print(f"⚠️  Evolution script returned {evo_result.returncode}")
    except Exception as e:
        print(f"⚠️  Evolution skipped: {e}")


def update_polished_home_html(existing_html, generated_html, archive_infos):
    archive_block = extract_between(
        generated_html,
        "<!-- Archive list -->",
        "<!-- Footer -->",
    )
    archive_data_block = json.dumps(archive_infos, ensure_ascii=False)

    updated = replace_between(
        existing_html,
        "<!-- Archive list -->",
        "<!-- Footer -->",
        archive_block,
    )
    updated = replace_between(
        updated,
        "const ALL_ARCHIVES = ",
        "\n\nconst LANG_STORAGE =",
        archive_data_block,
    )
    print(f"Updated: home.html ({len(archive_infos)} issues, polished preserved)")
    return updated


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate the AI Daily site from daily_data.json."
    )
    parser.add_argument(
        "--run-source-evolution",
        action="store_true",
        help="also run scripts/source_evolution.py after generating site files",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found. Please create daily_data.json first.")
        sys.exit(1)

    data = load_data()
    date_str = get_issue_date(data)
    today_str = current_beijing_date_str()

    html = build_html(data)

    # Write today.html (当天刊; 不是 index.html,见模块顶注释)
    today_path = BASE_DIR / TODAY_FILENAME
    previous_today = today_path.read_text(encoding="utf-8") if today_path.exists() else None
    today_path.write_text(html, encoding="utf-8")
    if previous_today is None:
        print(f"Generated: {today_path}")
    elif previous_today == html:
        print(f"Up-to-date: {today_path}")
    else:
        print(f"Updated: {today_path}")

    # Write archive page
    OUTPUT_DIR.mkdir(exist_ok=True)
    archive_path = OUTPUT_DIR / f"{date_str}.html"
    if archive_path.exists():
        previous_archive = archive_path.read_text(encoding="utf-8")
        if previous_archive == html:
            print(f"Up-to-date: {archive_path}")
        elif date_str == today_str:
            archive_path.write_text(html, encoding="utf-8")
            print(f"Updated: {archive_path} (today's issue refreshed)")
        else:
            print(f"Skipped: {archive_path} (historical archive preserved)")
    else:
        archive_path.write_text(html, encoding="utf-8")
        print(f"Generated: {archive_path}")

    # 用日期最新的一期覆盖 today.html，与首页列表第一条、/today 直链 三者一致
    # （Hermes 若只更新了较新的 archive、daily_data 仍滞后，否则会 4/24 vs 4/23 打架）
    sync_today_html_from_newest_archive()

    print(f"\nTotal items: {sum(len(data.get(k, [])) for k in ('research','github','models','community'))}")
    print("Done!")

    # ── 生成首页 home.html ─────────────────────────────
    print("\n🏠 Generating home page...")
    try:
        # 扫描所有归档日期（YYYY-MM-DD.html）并提取头条信息
        # 只保留 2026-04-15 及之后的归档
        MIN_DATE = "2026-04-15"
        archive_files = sorted(
            OUTPUT_DIR.glob("????-??-??.html"),
            key=lambda p: p.stem,
            reverse=True   # 最新日期排前面
        )
        archive_infos = []
        for p in archive_files:
            if p.stem < MIN_DATE:
                continue
            headline, total = extract_archive_meta(p)
            archive_infos.append((p.stem, headline, total))

        if archive_infos:
            home_path = BASE_DIR / "home.html"
            # 生成完整新页面（用于提取新存档列表）
            new_home_html = build_home_html(archive_infos)

            existing_home_html = home_path.read_text(encoding="utf-8") if home_path.exists() else ""
            if home_path.exists() and ("项目地图" in existing_home_html):
                # 精修版：只替换归档区和归档数据，保留顶部/样式/i18n
                polished = update_polished_home_html(
                    existing_home_html,
                    new_home_html,
                    archive_infos,
                )
                home_path.write_text(polished, encoding="utf-8")
            else:
                home_path.write_text(new_home_html, encoding="utf-8")
                print(f"Generated: {home_path} ({len(archive_infos)} issues)")
            # 打印头条预览
            for date_str, headline, total in archive_infos[:3]:
                print(f"  {date_str}: {headline[:50]}...")
        else:
            print("⚠️  No archives found, skipping home.html")
    except Exception as e:
        print(f"⚠️  Home page generation failed: {e}")

    if args.run_source_evolution:
        run_source_evolution()
    else:
        print("\nℹ️  Skipping source evolution (pass --run-source-evolution to enable)")


if __name__ == "__main__":
    main()
