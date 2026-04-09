#!/usr/bin/env python3
"""
AI Agent 日报 H5 页面生成器
读取 daily_data.json → 生成 index.html + 归档页面
"""
import json
import os
import sys
from html import escape
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "daily_data.json"
OUTPUT_DIR = BASE_DIR / "archives"

SECTION_META = {
    "research": {"icon": "🤖", "title": "AI Agent 研究"},
    "github":   {"icon": "⭐", "title": "GitHub 热门项目"},
    "models":   {"icon": "🚀", "title": "模型与行业动态"},
    "community": {"icon": "🔥", "title": "社区热议"},
}


def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def build_item_html(item):
    safe_title = escape(item.get("title", "Untitled"))
    safe_summary = escape(item.get("summary", ""))
    safe_link = escape(item.get("url", "#"), quote=True)
    tags = ""
    if item.get("tags"):
        tags = " ".join(
            f'<span class="tag">{escape(str(t))}</span>' for t in item["tags"]
        )
    return f"""
    <div class="card">
      <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="card-title">{safe_title}</a>
      <p class="card-summary">{safe_summary}</p>
      <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="read-more">查看原文</a>
      {tags}
    </div>"""


def build_section_html(key, items):
    meta = SECTION_META[key]
    section_id = f"section-{key}"
    cards = "\n".join(build_item_html(i) for i in items)
    return f"""
    <section class="section" id="{section_id}">
      <h2 class="section-title">{meta['icon']} {meta['title']}</h2>
      {cards}
    </section>"""


def build_html(data):
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
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
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
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
<meta property="og:url" content="https://lava-agent-daily.vercel.app">
<meta name="twitter:card" content="summary">
<title>AI Agent 日报 — {safe_date}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', 'Segoe UI', Roboto, sans-serif;
  background: #0a0a1a;
  color: #e0e0e0;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}}

/* Hero */
.hero {{
  background: linear-gradient(135deg, #0d1b2a 0%, #1b3a5c 40%, #2a5298 100%);
  padding: 48px 20px 36px;
  text-align: center;
  position: relative;
  overflow: hidden;
}}
.hero::after {{
  content: '';
  position: absolute;
  top: -50%; left: -50%;
  width: 200%; height: 200%;
  background: radial-gradient(circle at 30% 70%, rgba(99,179,237,0.08) 0%, transparent 50%);
  animation: pulse 8s ease-in-out infinite;
}}
@keyframes pulse {{ 50% {{ transform: scale(1.1); }} }}
.hero h1 {{
  font-size: 28px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 1px;
  position: relative;
  z-index: 1;
}}
.hero .date {{
  color: #7eb8e8;
  font-size: 14px;
  margin-top: 8px;
  position: relative;
  z-index: 1;
}}
.hero .stats {{
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 20px;
  position: relative;
  z-index: 1;
}}
.hero .stat {{
  text-align: center;
}}
.hero .stat-num {{
  font-size: 24px;
  font-weight: 700;
  color: #63b3ed;
}}
.hero .stat-label {{
  font-size: 11px;
  color: #7eb8e8;
  margin-top: 2px;
}}
.quick-nav {{
  max-width: 680px;
  margin: 0 auto;
  padding: 12px 16px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}}
.quick-link {{
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  text-decoration: none;
  color: #7eb8e8;
  background: rgba(126,184,232,0.12);
  border: 1px solid rgba(126,184,232,0.22);
  font-size: 12px;
  transition: all 0.2s;
}}
.quick-link:hover {{
  color: #d8ecff;
  background: rgba(126,184,232,0.2);
}}

/* Container */
.container {{
  max-width: 680px;
  margin: 0 auto;
  padding: 0 16px;
}}

/* Section */
.section {{
  margin-top: 28px;
}}
.section-title {{
  font-size: 17px;
  font-weight: 700;
  color: #a0c4ff;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(160,196,255,0.15);
  margin-bottom: 16px;
}}

/* Card */
.card {{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 14px;
  transition: background 0.2s, transform 0.15s;
}}
.card:active {{
  transform: scale(0.98);
  background: rgba(255,255,255,0.07);
}}
.card-title {{
  color: #e2e8f0;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.5;
  text-decoration: none;
  display: block;
}}
.card-title:hover {{
  color: #63b3ed;
}}
.card-summary {{
  color: #a0aec0;
  font-size: 13px;
  line-height: 1.75;
  margin-top: 8px;
}}
.read-more {{
  display: inline-block;
  margin-top: 8px;
  font-size: 12px;
  color: #7eb8e8;
  text-decoration: none;
}}
.read-more:hover {{
  color: #b8dbff;
}}
.tag {{
  display: inline-block;
  background: rgba(99,179,237,0.12);
  color: #63b3ed;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-top: 8px;
  margin-right: 6px;
}}

/* Share Bar */
.share-bar {{
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(13,27,42,0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid rgba(255,255,255,0.08);
  padding: 12px 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
  z-index: 100;
}}
.share-btn {{
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  color: #e0e0e0;
  padding: 10px 18px;
  border-radius: 24px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}}
.share-btn:hover {{
  background: rgba(255,255,255,0.14);
}}
.share-btn.primary {{
  background: linear-gradient(135deg, #07c160, #06ad56);
  border-color: transparent;
  color: #fff;
  font-weight: 600;
}}
.share-btn .icon {{ font-size: 16px; }}
.skip-link {{
  position: absolute;
  left: -9999px;
  top: 0;
  z-index: 1000;
}}
.skip-link:focus {{
  left: 12px;
  top: 12px;
  padding: 8px 12px;
  color: #fff;
  background: #1b3a5c;
  border-radius: 8px;
}}

/* Footer */
.footer {{
  text-align: center;
  padding: 32px 20px 90px;
  color: #4a5568;
  font-size: 12px;
  line-height: 1.8;
}}
.footer a {{
  color: #63b3ed;
  text-decoration: none;
}}

/* Toast */
.toast {{
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.9);
  background: rgba(0,0,0,0.85);
  color: #fff;
  padding: 14px 28px;
  border-radius: 10px;
  font-size: 14px;
  z-index: 200;
  opacity: 0;
  transition: all 0.25s ease;
  pointer-events: none;
}}
.toast.show {{
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}}

/* WeChat Modal */
.modal-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 300;
  justify-content: center;
  align-items: center;
}}
.modal-overlay.show {{ display: flex; }}
.modal {{
  background: #fff;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  max-width: 300px;
  width: 90%;
}}
.modal h3 {{
  color: #333;
  font-size: 16px;
  margin-bottom: 16px;
}}
.modal .qr-placeholder {{
  width: 180px;
  height: 180px;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 13px;
}}
.modal .qr-placeholder img {{
  width: 100%;
  height: 100%;
  border-radius: 8px;
  display: block;
}}
.modal .close-btn {{
  background: #f0f0f0;
  border: none;
  padding: 10px 32px;
  border-radius: 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}}
</style>
</head>
<body>
<a href="#main-content" class="skip-link">跳到正文</a>

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
  <a href="images/{safe_date}.png" download="AI-Agent日报-{safe_date}.png" class="share-btn primary" style="text-decoration:none;">
    <span class="icon">📸</span> 保存图片
  </a>
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
const SHARE_URL = 'https://lava-agent-daily.vercel.app';

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

function nativeShare() {{
  if (navigator.share) {{
    navigator.share({{
      title: document.title,
      text: 'AI Agent 日报 — 今日 AI 资讯精选',
      url: SHARE_URL
    }}).catch(() => {{}});
  }} else {{
    copyLink();
  }}
}}
</script>

</body>
</html>"""


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found. Please create daily_data.json first.")
        sys.exit(1)

    data = load_data()
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    html = build_html(data)

    # Write index.html (latest)
    index_path = BASE_DIR / "index.html"
    with open(index_path, "w") as f:
        f.write(html)
    print(f"Generated: {index_path}")

    # Write archive page
    OUTPUT_DIR.mkdir(exist_ok=True)
    archive_path = OUTPUT_DIR / f"{date_str}.html"
    with open(archive_path, "w") as f:
        f.write(html)
    print(f"Generated: {archive_path}")

    print(f"\nTotal items: {sum(len(data.get(k, [])) for k in ('research','github','models','community'))}")
    print("Done!")


if __name__ == "__main__":
    main()
