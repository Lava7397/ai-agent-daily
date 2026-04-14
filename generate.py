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

/* ---- Hero / 莫比斯封面 ---- */
.hero {{
  background:
    radial-gradient(ellipse at 20% 80%, rgba(178,200,218,0.35) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(210,185,220,0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(245,235,210,0.5) 0%, transparent 70%),
    #f5f0e8;
  padding: 56px 24px 44px;
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
