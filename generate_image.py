#!/usr/bin/env python3
"""
AI Agent 日报 — 分享图片生成器
可爱的动漫风格，支持一键生成，带 LavaDaily 水印
"""
import json
import math
import textwrap
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "daily_data.json"
OUTPUT_DIR = BASE_DIR / "images"

# --- 小清新配色 (cute pastel anime palette) ---
COLORS = {
    "bg_top":       (255, 230, 243),   # 粉色渐变上
    "bg_bottom":    (230, 240, 255),   # 蓝色渐变下
    "card":         (255, 255, 255),   # 白色卡片
    "card_shadow":  (220, 210, 230),   # 卡片阴影
    "header":       (120, 80, 160),    # 紫色标题
    "section_bg":   (245, 240, 255),   # 板块背景
    "section_text": (100, 70, 140),    # 板块标题
    "title":        (60, 50, 80),      # 正文标题
    "summary":      (120, 110, 135),   # 摘要文字
    "tag_bg":       (255, 220, 240),   # 标签背景
    "tag_text":     (180, 80, 130),    # 标签文字
    "watermark":    (200, 180, 215),   # 水印
    "date_text":    (150, 130, 170),   # 日期
    "divider":      (235, 225, 245),   # 分隔线
    "star":         (255, 200, 50),    # 星星
    "accent1":      (255, 150, 180),   # 粉色强调
    "accent2":      (150, 200, 255),   # 蓝色强调
    "accent3":      (180, 230, 150),   # 绿色强调
    "accent4":      (255, 200, 150),   # 橙色强调
}

SECTION_META = {
    "research":  {"icon": "🤖", "title": "AI Agent 研究", "accent": "accent1"},
    "github":    {"icon": "⭐", "title": "GitHub 热门项目", "accent": "accent2"},
    "models":    {"icon": "🚀", "title": "模型与行业动态", "accent": "accent3"},
    "community": {"icon": "🔥", "title": "社区热议", "accent": "accent4"},
}

# Image layout
WIDTH = 1080
PADDING = 48
CARD_RADIUS = 24
CARD_PADDING = 32
SECTION_GAP = 36
ITEM_GAP = 20


def load_fonts():
    """Load fonts with fallback."""
    font_paths = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    emoji_paths = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",
    ]

    font_regular = None
    font_bold = None
    font_emoji = None

    for fp in font_paths:
        try:
            font_regular = ImageFont.truetype(fp, 32)
            font_bold = ImageFont.truetype(fp, 38)
            break
        except Exception:
            continue

    if not font_regular:
        font_regular = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    for ep in emoji_paths:
        try:
            font_emoji = ImageFont.truetype(ep, 34)
            break
        except Exception:
            continue
    if not font_emoji:
        font_emoji = font_regular

    return {
        "title": ImageFont.truetype(font_paths[0], 52) if font_paths else font_bold,
        "date": ImageFont.truetype(font_paths[0], 28) if font_paths else font_regular,
        "section": ImageFont.truetype(font_paths[0], 32) if font_paths else font_bold,
        "item_title": font_bold,
        "item_summary": font_regular,
        "tag": ImageFont.truetype(font_paths[0], 22) if font_paths else font_regular,
        "watermark": ImageFont.truetype(font_paths[0], 24) if font_paths else font_regular,
        "emoji": font_emoji,
        "stats": ImageFont.truetype(font_paths[0], 26) if font_paths else font_regular,
    }


def text_height(text, font, max_width):
    """Calculate rendered text height for wrapped text."""
    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    lines = textwrap.wrap(text, width=max_width)
    if not lines:
        return 0
    bbox = draw.textbbox((0, 0), "测", font=font)
    line_h = bbox[3] - bbox[1] + 6
    return line_h * len(lines)


def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_gradient_bg(img, color_top, color_bottom):
    """Draw vertical gradient background."""
    w, h = img.size
    for y in range(h):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / h)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / h)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / h)
        draw = ImageDraw.Draw(img)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def draw_stars(draw, y_start, count=5):
    """Draw cute decorative stars."""
    positions = [
        (80, y_start + 10), (200, y_start - 5),
        (900, y_start + 8), (980, y_start - 3),
        (500, y_start + 15),
    ]
    for i, (x, y) in enumerate(positions[:count]):
        size = 6 + (i % 3) * 3
        color = COLORS["star"] if i % 2 == 0 else COLORS["accent1"]
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width pixels."""
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        words = list(paragraph)  # Character by character for CJK
        current_line = ""
        for char in words:
            test = current_line + char
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width and current_line:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test
        if current_line:
            lines.append(current_line)
    return lines


def calculate_section_height(items, fonts, content_width):
    """Calculate total height needed for a section."""
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    h = 24 + 40 + 16  # padding + section title + gap
    for item in items:
        h += 16  # item top padding
        # Title
        title_lines = wrap_text(item["title"], fonts["item_title"], content_width - 32, draw)
        h += len(title_lines) * 42
        h += 8
        # Summary (≤100 chars, 1-2 lines)
        summary = item.get("summary", "")[:100]
        summary_lines = wrap_text(summary, fonts["item_summary"], content_width - 32, draw)
        h += len(summary_lines) * 36
        # Tags
        h += 32
        h += 16  # bottom padding
    return h


def generate():
    with open(DATA_FILE) as f:
        data = json.load(f)

    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    fonts = load_fonts()
    draw_dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    # Calculate total height
    total_height = 0
    # Header
    total_height += 200
    # Stats bar
    total_height += 80
    # Sections
    sections_order = ["research", "github", "models", "community"]
    for key in sections_order:
        items = data.get(key, [])
        if items:
            content_width = WIDTH - PADDING * 2 - CARD_PADDING * 2
            total_height += calculate_section_height(items, fonts, content_width) + SECTION_GAP
    # Footer
    total_height += 80

    # Create image
    img = Image.new("RGB", (WIDTH, total_height), COLORS["bg_top"])
    draw_gradient_bg(img, COLORS["bg_top"], COLORS["bg_bottom"])
    draw = ImageDraw.Draw(img)

    y = 0

    # --- Header ---
    y += 40
    # Title
    title = "AI Agent 日报"
    bbox = draw.textbbox((0, 0), title, font=fonts["title"])
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, y), title, fill=COLORS["header"], font=fonts["title"])
    y += 65

    # Date
    date_display = f"📅 {date_str} · 每日精选"
    bbox = draw.textbbox((0, 0), date_display, font=fonts["date"])
    dw = bbox[2] - bbox[0]
    draw.text(((WIDTH - dw) // 2, y), date_display, fill=COLORS["date_text"], font=fonts["date"])
    y += 50

    # Decorative stars
    draw_stars(draw, y, 5)
    y += 30

    # --- Stats bar ---
    stats = [
        (str(sum(len(data.get(k, [])) for k in sections_order)), "条资讯"),
        (str(sum(1 for k in sections_order if data.get(k, []))), "个板块"),
        (str(len(data.get("sources", "").split(","))), "个来源"),
    ]
    stat_total_w = 0
    stat_items = []
    for num, label in stats:
        text = f"{num} {label}"
        bbox = draw.textbbox((0, 0), text, font=fonts["stats"])
        sw = bbox[2] - bbox[0]
        stat_items.append((text, sw))
        stat_total_w += sw + 60
    stat_total_w -= 60

    sx = (WIDTH - stat_total_w) // 2
    for text, sw in stat_items:
        draw.text((sx, y), text, fill=COLORS["section_text"], font=fonts["stats"])
        sx += sw + 60
    y += 60

    # --- Sections ---
    for sec_idx, key in enumerate(sections_order):
        items = data.get(key, [])
        if not items:
            continue

        meta = SECTION_META[key]
        accent_color = COLORS[meta["accent"]]
        content_width = WIDTH - PADDING * 2 - CARD_PADDING * 2

        # Section card
        sec_height = calculate_section_height(items, fonts, content_width)
        card_x1, card_y1 = PADDING, y
        card_x2, card_y2 = WIDTH - PADDING, y + sec_height

        # Shadow
        draw_rounded_rect(draw, (card_x1 + 4, card_y1 + 4, card_x2 + 4, card_y2 + 4),
                          CARD_RADIUS, COLORS["card_shadow"])
        # Card
        draw_rounded_rect(draw, (card_x1, card_y1, card_x2, card_y2),
                          CARD_RADIUS, COLORS["card"])
        # Accent bar on left
        draw_rounded_rect(draw, (card_x1, card_y1, card_x1 + 8, card_y2),
                          4, accent_color)

        cy = card_y1 + 24
        # Section icon + title
        section_title = f"{meta['icon']} {meta['title']}"
        draw.text((card_x1 + CARD_PADDING, cy), section_title,
                  fill=COLORS["section_text"], font=fonts["section"])
        cy += 48

        # Divider
        draw.line([(card_x1 + CARD_PADDING, cy), (card_x2 - CARD_PADDING, cy)],
                  fill=COLORS["divider"], width=2)
        cy += 16

        # Items
        for item_idx, item in enumerate(items):
            item_x = card_x1 + CARD_PADDING
            cy += 16

            # Title
            title_lines = wrap_text(item["title"], fonts["item_title"], content_width - 16, draw)
            for line in title_lines:
                draw.text((item_x, cy), line, fill=COLORS["title"], font=fonts["item_title"])
                cy += 42

            cy += 4

            # Summary (≤100 chars)
            summary = item.get("summary", "")[:100]
            summary_lines = wrap_text(summary, fonts["item_summary"], content_width - 16, draw)
            for line in summary_lines:
                draw.text((item_x, cy), line, fill=COLORS["summary"], font=fonts["item_summary"])
                cy += 36

            # Tags
            tag_x = item_x
            tag_y = cy + 4
            for tag in item.get("tags", []):
                tag_text = f" {tag} "
                bbox = draw.textbbox((0, 0), tag_text, font=fonts["tag"])
                tw = bbox[2] - bbox[0] + 16
                th = bbox[3] - bbox[1] + 10
                draw_rounded_rect(draw, (tag_x, tag_y, tag_x + tw, tag_y + th),
                                  10, COLORS["tag_bg"])
                draw.text((tag_x + 8, tag_y + 3), tag_text,
                          fill=COLORS["tag_text"], font=fonts["tag"])
                tag_x += tw + 10

            cy = tag_y + 32

            # Item divider (except last)
            if item_idx < len(items) - 1:
                draw.line([(item_x, cy - 8), (card_x2 - CARD_PADDING, cy - 8)],
                          fill=COLORS["divider"], width=1)

        y = card_y2 + SECTION_GAP

    # --- Footer ---
    footer_y = y + 10
    sources = data.get("sources", "")
    footer_text = f"数据来源：{sources}"
    bbox = draw.textbbox((0, 0), footer_text, font=fonts["date"])
    fw = bbox[2] - bbox[0]
    draw.text(((WIDTH - fw) // 2, footer_y), footer_text,
              fill=COLORS["date_text"], font=fonts["date"])
    footer_y += 35

    gen_text = f"Hermes Agent 自动生成 · 每日 09:00 更新"
    bbox = draw.textbbox((0, 0), gen_text, font=fonts["date"])
    gw = bbox[2] - bbox[0]
    draw.text(((WIDTH - gw) // 2, footer_y), gen_text,
              fill=COLORS["date_text"], font=fonts["date"])

    # --- Watermark ---
    wm_text = "✦ LavaDaily ✦"
    bbox = draw.textbbox((0, 0), wm_text, font=fonts["watermark"])
    ww = bbox[2] - bbox[0]
    wh = bbox[3] - bbox[1]
    wm_x = (WIDTH - ww) // 2
    wm_y = total_height - 50
    # Draw watermark with slight transparency effect (lighter color)
    draw.text((wm_x, wm_y), wm_text, fill=COLORS["watermark"], font=fonts["watermark"])

    # Save
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"{date_str}.png"
    img.save(str(output_path), "PNG", quality=95)
    print(f"Generated: {output_path}")
    print(f"Size: {img.size[0]}x{img.size[1]}px")
    return str(output_path)


if __name__ == "__main__":
    path = generate()
    print(f"\nImage saved to: {path}")
