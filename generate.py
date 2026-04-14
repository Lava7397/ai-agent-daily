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
  font-family: 'Courier New', 'SF Mono', Monaco, monospace;
  background: #0a0a0a;
  background-image: 
    repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.02) 2px, rgba(255,255,255,0.02) 4px);
  color: #d4c5a9;
  min-height: 10vh;
  -webkit-font-smoothing: antialiased;
}}

/* Hero - 废土风格 */
.hero {{
  background: linear-gradient(180deg, #1a1510 0%, #0d0b08 50%, #0a0a0a 100%);
  padding: 48px 20px 36px;
  text-align: center;
  position: relative;
  overflow: hidden;
  border-bottom: 3px solid #c9a227;
  box-shadow: 0 4px 30px rgba(201, 162, 39, 0.3);
}}
.hero::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0 L60 30 L30 60 L0 30 Z' fill='none' stroke='%23c9a227' stroke-width='0.5' opacity='0.1'/%3E%3C/svg%3E");
  opacity: 0.3;
}}
.hero::after {{
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 100px;
  background: linear-gradient(0deg, #0a0a0a 0%, transparent 100%);
}}
.hero h1 {{
  font-size: 32px;
  font-weight: 800;
  color: #c9a227;
  letter-spacing: 4px;
  text-transform: uppercase;
  position: relative;
  z-index: 1;
  text-shadow: 0 0 20px rgba(201, 162, 39, 0.5), 0 0 40px rgba(201, 162, 39, 0.3);
}}
.hero .date {{
  color: #8b7355;
  font-size: 13px;
  margin-top: 12px;
  position: relative;
  z-index: 1;
  letter-spacing: 2px;
}}
.hero .stats {{
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-top: 24px;
  position: relative;
  z-index: 1;
}}
.hero .stat {{
  text-align: center;
  border: 1px solid rgba(201, 162, 39, 0.3);
  padding: 12px 20px;
  background: rgba(0, 0, 0, 0.5);
}}
.hero .stat-num {{
  font-size: 28px;
  font-weight: 700;
  color: #e8d5a3;
  font-family: 'Courier New', monospace;
}}
.hero .stat-label {{
  font-size: 10px;
  color: #8b7355;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

.quick-nav {{
  max-width: 720px;
  margin: 0 auto;
  padding: 16px 16px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}}
.quick-link {{
  display: inline-block;
  padding: 8px 14px;
  text-decoration: none;
  color: #c9a227;
  background: transparent;
  border: 1px solid #c9a227;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s;
}}
.quick-link:hover {{
  color: #0a0a0a;
  background: #c9a227;
  box-shadow: 0 0 15px rgba(201, 162, 39, 0.5);
}}

/* Container */
.container {{
  max-width: 720px;
  margin: 0 auto;
  padding: 0 16px 100px;
}}

/* Section */
.section {{
  margin-top: 40px;
}}
.section-title {{
  font-size: 16px;
  font-weight: 700;
  color: #c9a227;
  padding: 14px 20px;
  background: linear-gradient(90deg, rgba(201, 162, 39, 0.18) 0%, transparent 100%);
  border-left: 4px solid #c9a227;
  margin-bottom: 24px;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-family: 'Courier New', monospace;
}}

/* Card - 废土风格 */
.card {{
  background: rgba(26, 21, 16, 0.8);
  border: 1px solid rgba(201, 162, 39, 0.2);
  border-left: 3px solid #8b7355;
  padding: 26px;
  margin-bottom: 24px;
  transition: all 0.3s;
  position: relative;
}}
.card::before {{
  content: '▸';
  position: absolute;
  left: -20px;
  top: 20px;
  color: #c9a227;
  font-size: 12px;
}}
.card:hover {{
  border-left-color: #c9a227;
  background: rgba(201, 162, 39, 0.05);
  transform: translateX(4px);
  box-shadow: -4px 0 20px rgba(201, 162, 39, 0.2);
}}
.card-title {{
  color: #e8d5a3;
  font-size: 17px;
  font-weight: 600;
  line-height: 1.6;
  text-decoration: none;
  display: block;
  font-family: 'Courier New', monospace;
}}
.card-title:hover {{
  color: #c9a227;
  text-shadow: 0 0 10px rgba(201, 162, 39, 0.5);
}}
.card-summary {{
  color: #9a8b70;
  font-size: 14px;
  line-height: 2.0;
  margin-top: 14px;
  border-top: 1px dashed rgba(139, 115, 85, 0.3);
  padding-top: 14px;
}}
.read-more {{
  display: inline-block;
  margin-top: 14px;
  font-size: 12px;
  color: #c9a227;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 1px;
  border: 1px solid #c9a227;
  padding: 7px 14px;
  transition: all 0.3s;
}}
.read-more:hover {{
  background: #c9a227;
  color: #0a0a0a;
}}
.tag {{
  display: inline-block;
  background: rgba(201, 162, 39, 0.12);
  color: #c9a227;
  font-size: 12px;
  padding: 5px 12px;
  margin-top: 14px;
  margin-right: 8px;
  border: 1px solid rgba(201, 162, 39, 0.35);
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

/* Share Bar */
.share-bar {{
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(10, 10, 10, 0.98);
  border-top: 2px solid #c9a227;
  padding: 14px 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
  z-index: 100;
  box-shadow: 0 -4px 30px rgba(201, 162, 39, 0.2);
}}
.share-btn {{
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1px solid #8b7355;
  color: #d4c5a9;
  padding: 12px 20px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
  -webkit-tap-highlight-color: transparent;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
}}
.share-btn:hover {{
  border-color: #c9a227;
  color: #c9a227;
  box-shadow: 0 0 20px rgba(201, 162, 39, 0.3);
}}
.share-btn.primary {{
  background: #c9a227;
  border-color: #c9a227;
  color: #0a0a0a;
  font-weight: 700;
}}
.share-btn.primary:hover {{
  background: #e8d5a3;
  box-shadow: 0 0 30px rgba(201, 162, 39, 0.6);
}}
.share-btn .icon {{ font-size: 16px; }}

.skip-link {{
  position: absolute;
  top: -40px;
  left: 0;
  background: #c9a227;
  color: #0a0a0a;
  padding: 8px 16px;
  z-index: 1000;
  font-family: 'Courier New', monospace;
}}
.skip-link:focus {{ top: 0; }}

/* Footer */
.footer {{
  max-width: 720px;
  margin: 0 auto;
  padding: 24px 16px;
  text-align: center;
  color: #5a4d3a;
  font-size: 11px;
  border-top: 1px solid rgba(139, 115, 85, 0.2);
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

/* Toast */
.toast {{
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%) translateY(20px);
  background: #c9a227;
  color: #0a0a0a;
  padding: 12px 24px;
  border-radius: 0;
  font-size: 13px;
  font-weight: 600;
  opacity: 0;
  transition: all 0.3s;
  z-index: 200;
  font-family: 'Courier New', monospace;
  box-shadow: 0 4px 20px rgba(201, 162, 39, 0.5);
}}
.toast.show {{
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}}

/* Modal */
.modal-overlay {{
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.9);
  display: none;
  justify-content: center;
  align-items: center;
  z-index: 300;
}}
.modal-overlay.show {{ display: flex; }}
.modal {{
  background: #1a1510;
  border: 2px solid #c9a227;
  padding: 32px;
  max-width: 320px;
  width: 90%;
  text-align: center;
}}
.modal h3 {{
  color: #c9a227;
  margin-bottom: 20px;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  letter-spacing: 2px;
}}
.qr-placeholder {{
  width: 200px;
  height: 200px;
  margin: 0 auto 20px;
  background: rgba(201, 162, 39, 0.1);
  border: 1px dashed #c9a227;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8b7355;
  font-size: 12px;
}}
.qr-placeholder img {{ max-width: 100%; }}
.close-btn {{
  background: transparent;
  border: 1px solid #c9a227;
  color: #c9a227;
  padding: 10px 24px;
  cursor: pointer;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s;
}}
.close-btn:hover {{
  background: #c9a227;
  color: #0a0a0a;
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

function nativeShare() {{\n  if (navigator.share) {{\n    navigator.share({{\n      title: document.title,\n      text: 'AI Agent 日报 — 今日 AI 资讯精选',\n      url: SHARE_URL\n    }}).catch(() => {{}});\n  }} else {{\n    copyLink();\n  }}\n}}\n\nfunction downloadImage() {{\n  const date = '{safe_date}';\n  const imageUrl = `images/${{date}}.png`;\n  const fileName = `AI-Agent日报-${{date}}.png`;\n  \n  // 尝试使用 fetch 下载（解决跨域问题）\n  fetch(imageUrl)\n    .then(response => response.blob())\n    .then(blob => {{\n      const url = window.URL.createObjectURL(blob);\n      const a = document.createElement('a');\n      a.href = url;\n      a.download = fileName;\n      document.body.appendChild(a);\n      a.click();\n      document.body.removeChild(a);\n      window.URL.revokeObjectURL(url);\n      showToast('📸 图片开始下载');\n    }})\n    .catch(() => {{\n      // 如果 fetch 失败，直接打开图片\n      window.open(imageUrl, '_blank');\n      showToast('已在新窗口打开图片，长按保存');\n    }});\n}}
</script>

</body>
</html>"""



def build_email_html(data):
    """生成邮件专用 HTML，使用绝对 URL"""
    html = build_html(data)
    
    # 将相对图片路径替换为绝对 URL
    base_url = "https://ai-agent-daily-phi.vercel.app"
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    
    # 替换图片 URL
    html = html.replace(f'images/{date_str}.png', f'{base_url}/images/{date_str}.png')
    
    # 添加邮件特定的样式修复
    email_styles = """
<style>
  /* 邮件客户端兼容性修复 */
  body { margin: 0 !important; padding: 0 !important; }
  .share-bar { position: relative !important; margin-top: 30px; }
  .card { page-break-inside: avoid; }
  img { max-width: 100%; height: auto; }
</style>
"""
    html = html.replace('</head>', email_styles + '</head>')
    
    return html


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found. Please create daily_data.json first.")
        sys.exit(1)

    data = load_data()
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    html = build_html(data)
    email_html = build_email_html(data)

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

    # Write email version
    email_path = BASE_DIR / "email.html"
    with open(email_path, "w") as f:
        f.write(email_html)
    print(f"Generated: {email_path}")

    print(f"\nTotal items: {sum(len(data.get(k, [])) for k in ('research','github','models','community'))}")
    print("Done!")


if __name__ == "__main__":
    main()
