#!/usr/bin/env python3
"""
LavaAgent 今日刊 — 分享图片生成器
中性色调 + 宫崎骏风格边角装饰，带 LavaDaily 水印
"""
import json
import math
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "daily_data.json"
OUTPUT_DIR = BASE_DIR / "images"

# --- 莫比斯废土科幻色调 (Moebius Wasteland Palette) ---
COLORS = {
    "bg_top":       (10, 10, 10),         # 纯黑背景
    "bg_bottom":    (15, 12, 8),          # 深棕黑
    "card":         (26, 21, 16),         # 废土棕卡片
    "card_border":  (139, 115, 85),       # 土黄边框
    "card_shadow":  (201, 162, 39),       # 金色阴影
    "header":       (201, 162, 39),       # 金色标题
    "section_text": (201, 162, 39),       # 金色板块标题
    "title":        (232, 213, 163),      # 暖金标题
    "summary":      (154, 139, 112),      # 土黄摘要
    "tag_bg":       (201, 162, 39),       # 金色标签背景
    "tag_text":     (10, 10, 10),         # 黑色标签文字
    "watermark":    (90, 75, 50),         # 暗金水印
    "date_text":    (139, 115, 85),       # 土黄日期
    "divider":      (201, 162, 39),       # 金线分隔
    "accent1":      (201, 162, 39),       # 金色（研究）
    "accent2":      (201, 162, 39),       # 金色（GitHub）
    "accent3":      (201, 162, 39),       # 金色（模型）
    "accent4":      (201, 162, 39),       # 金色（社区）
    "moebius_line": (201, 162, 39),       # 莫比斯线条
    "moebius_dark": (26, 21, 16),         # 深色区域
    "moebius_glow": (232, 213, 163),      # 发光效果
}

SECTION_META = {
    "research":  {"icon": "🤖", "title": "AI Agent 研究", "accent": "accent1"},
    "github":    {"icon": "⭐", "title": "GitHub 热门项目", "accent": "accent2"},
    "models":    {"icon": "🚀", "title": "模型与行业动态", "accent": "accent3"},
    "community": {"icon": "🔥", "title": "社区热议", "accent": "accent4"},
}

WIDTH = 1080
PADDING = 48
CARD_RADIUS = 20
CARD_PADDING = 36
SECTION_GAP = 40


def load_fonts():
    font_paths = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    emoji_paths = ["/System/Library/Fonts/Apple Color Emoji.ttc"]

    font_regular = font_bold = font_emoji = None
    for fp in font_paths:
        try:
            font_regular = ImageFont.truetype(fp, 32)
            font_bold = ImageFont.truetype(fp, 38)
            break
        except Exception:
            continue
    if not font_regular:
        font_regular = font_bold = ImageFont.load_default()
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
        "watermark": ImageFont.truetype(font_paths[0], 22) if font_paths else font_regular,
        "emoji": font_emoji,
        "stats": ImageFont.truetype(font_paths[0], 26) if font_paths else font_regular,
    }


def wrap_text(text, font, max_width, draw):
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        current_line = ""
        for char in paragraph:
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


def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


# ====== 宫崎骏风格装饰元素 ======

def draw_moebius_line(draw, x, y, size=20, angle=0, color=None):
    """绘制莫比斯风格的线条"""
    if color is None:
        color = COLORS["moebius_line"]
    import math
    end_x = x + size * math.cos(math.radians(angle))
    end_y = y + size * math.sin(math.radians(angle))
    draw.line([(x, y), (end_x, end_y)], fill=color, width=2)
    draw.ellipse([end_x-3, end_y-3, end_x+3, end_y+3], fill=color)


def draw_moebius_pattern(draw, cx, cy, size=40, color=None):
    """绘制莫比斯风格的几何图案"""
    if color is None:
        color = COLORS["moebius_line"]
    # 绘制菱形图案
    points = [(cx, cy-size), (cx+size, cy), (cx, cy+size), (cx-size, cy)]
    draw.polygon(points, outline=color, width=2)
    # 内部菱形
    inner_size = size * 0.5
    inner_points = [(cx, cy-inner_size), (cx+inner_size, cy), (cx, cy+inner_size), (cx-inner_size, cy)]
    draw.polygon(inner_points, outline=color, width=1)


def draw_moebius_dots(draw, x, y, count=3, color=None):
    """绘制莫比斯风格的点阵"""
    if color is None:
        color = COLORS["moebius_line"]
    for i in range(count):
        dot_x = x + i * 15
        dot_y = y
        draw.ellipse([dot_x-4, dot_y-4, dot_x+4, dot_y+4], fill=color)


def draw_moebius_corner_decoration(draw, width, height, corner):
    """绘制莫比斯风格的角落装饰"""
    if corner == "top-left":
        draw_moebius_line(draw, 30, 30, size=80, angle=45)
        draw_moebius_line(draw, 50, 20, size=60, angle=0)
        draw_moebius_dots(draw, 20, 60, count=3)
    elif corner == "top-right":
        draw_moebius_line(draw, width-30, 30, size=80, angle=135)
        draw_moebius_line(draw, width-50, 20, size=60, angle=180)
        draw_moebius_dots(draw, width-80, 60, count=3)
    elif corner == "bottom-left":
        draw_moebius_line(draw, 30, height-30, size=80, angle=-45)
        draw_moebius_pattern(draw, 60, height-60, size=30)
    elif corner == "bottom-right":
        draw_moebius_line(draw, width-30, height-30, size=80, angle=-135)
        draw_moebius_pattern(draw, width-60, height-60, size=30)


def draw_moebius_header_decorations(draw, y_center):
    """绘制莫比斯风格的标题装饰"""
    color = COLORS["moebius_line"]
    # 绘制水平装饰线
    draw.line([(100, y_center), (WIDTH-100, y_center)], fill=color, width=1)
    # 绘制端点装饰
    draw_moebius_pattern(draw, 80, y_center, size=15, color=color)
    draw_moebius_pattern(draw, WIDTH-80, y_center, size=15, color=color)




def draw_gradient_bg(img, color_top, color_bottom):
    """绘制柔和的渐变背景"""
    w, h = img.size
    for y_pos in range(h):
        ratio = y_pos / h
        # 使用缓动函数让渐变更自然
        t = ratio * ratio * (3 - 2 * ratio)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        ImageDraw.Draw(img).line([(0, y_pos), (w, y_pos)], fill=(r, g, b))


def calculate_section_height(items, fonts, content_width):
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    h = 24 + 40 + 16
    for item in items:
        h += 16
        title_lines = wrap_text(item["title"], fonts["item_title"], content_width - 32, draw)
        h += len(title_lines) * 42
        h += 8
        summary = item.get("summary", "")[:100]
        summary_lines = wrap_text(summary, fonts["item_summary"], content_width - 32, draw)
        h += len(summary_lines) * 36
        h += 32
        h += 16
    return h


def generate():
    with open(DATA_FILE) as f:
        data = json.load(f)

    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    fonts = load_fonts()

    sections_order = ["research", "github", "models", "community"]

    # Calculate total height
    total_height = 200 + 80  # header + stats
    for key in sections_order:
        items = data.get(key, [])
        if items:
            content_width = WIDTH - PADDING * 2 - CARD_PADDING * 2
            total_height += calculate_section_height(items, fonts, content_width) + SECTION_GAP
    total_height += 100  # footer

    # Add space for corner decorations
    total_height += 20

    # Create image with gradient background
    img = Image.new("RGB", (WIDTH, total_height), COLORS["bg_top"])
    draw_gradient_bg(img, COLORS["bg_top"], COLORS["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # ====== 四角宫崎骏装饰 ======
    draw_moebius_corner_decoration(draw, WIDTH, total_height, "top-left")
    draw_moebius_corner_decoration(draw, WIDTH, total_height, "top-right")

    y = 0

    # ====== Header ======
    y += 50
    title = "LavaAgent 今日刊"
    bbox = draw.textbbox((0, 0), title, font=fonts["title"])
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, y), title, fill=COLORS["header"], font=fonts["title"])
    y += 65

    date_display = f"{date_str} · 每日精选"
    bbox = draw.textbbox((0, 0), date_display, font=fonts["date"])
    dw = bbox[2] - bbox[0]
    draw.text(((WIDTH - dw) // 2, y), date_display, fill=COLORS["date_text"], font=fonts["date"])
    y += 45

    # 标题装饰
    draw_moebius_header_decorations(draw, y - 30)
    y += 20

    # ====== Stats bar ======
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

    # ====== Sections ======
    for sec_idx, key in enumerate(sections_order):
        items = data.get(key, [])
        if not items:
            continue

        meta = SECTION_META[key]
        accent_color = COLORS[meta["accent"]]
        content_width = WIDTH - PADDING * 2 - CARD_PADDING * 2

        sec_height = calculate_section_height(items, fonts, content_width)
        card_x1, card_y1 = PADDING, y
        card_x2, card_y2 = WIDTH - PADDING, y + sec_height

        # 卡片阴影
        draw_rounded_rect(draw, (card_x1 + 3, card_y1 + 3, card_x2 + 3, card_y2 + 3),
                          CARD_RADIUS, COLORS["card_shadow"])
        # 卡片主体
        draw_rounded_rect(draw, (card_x1, card_y1, card_x2, card_y2),
                          CARD_RADIUS, COLORS["card"],
                          outline=COLORS["card_border"], width=1)

        # 左侧装饰条（模拟吉卜力风格的木质条）
        draw_rounded_rect(draw, (card_x1, card_y1 + 10, card_x1 + 6, card_y2 - 10),
                          3, accent_color)

        # 板块右上角小装饰（像吉卜力动画里的小点缀）
        decor_x = card_x2 - 50
        decor_y = card_y1 + 20
        draw_moebius_line(draw, decor_x, decor_y, size=8, angle=45, color=accent_color)
        draw_moebius_line(draw, decor_x + 15, decor_y + 5, size=6, angle=60, color=accent_color)

        cy = card_y1 + 24
        # Section title
        section_title = f"{meta['icon']} {meta['title']}"
        draw.text((card_x1 + CARD_PADDING, cy), section_title,
                  fill=COLORS["section_text"], font=fonts["section"])
        cy += 48

        # Divider with dots (Ghibli-style dotted line)
        div_start = card_x1 + CARD_PADDING
        div_end = card_x2 - CARD_PADDING
        for dx in range(div_start, div_end, 8):
            draw.ellipse([dx, cy - 1, dx + 2, cy + 1], fill=COLORS["divider"])
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

            # Item divider
            if item_idx < len(items) - 1:
                for dx in range(item_x, card_x2 - CARD_PADDING, 12):
                    draw.ellipse([dx, cy - 8, dx + 2, cy - 6], fill=COLORS["divider"])

        y = card_y2 + SECTION_GAP

    # ====== 底部角落装饰 ======
    draw_moebius_corner_decoration(draw, WIDTH, total_height, "bottom-left")
    draw_moebius_corner_decoration(draw, WIDTH, total_height, "bottom-right")

    # ====== Footer ======
    footer_y = y + 15
    sources = data.get("sources", "")
    footer_text = f"数据来源：{sources}"
    bbox = draw.textbbox((0, 0), footer_text, font=fonts["date"])
    fw = bbox[2] - bbox[0]
    draw.text(((WIDTH - fw) // 2, footer_y), footer_text,
              fill=COLORS["date_text"], font=fonts["date"])
    footer_y += 35

    gen_text = "Hermes Agent 自动生成 · 每日北京时间 11:30 更新"
    bbox = draw.textbbox((0, 0), gen_text, font=fonts["date"])
    gw = bbox[2] - bbox[0]
    draw.text(((WIDTH - gw) // 2, footer_y), gen_text,
              fill=COLORS["date_text"], font=fonts["date"])

    # ====== Watermark ======
    wm_text = "✦ LavaDaily ✦"
    bbox = draw.textbbox((0, 0), wm_text, font=fonts["watermark"])
    ww = bbox[2] - bbox[0]
    wm_x = (WIDTH - ww) // 2
    wm_y = total_height - 45
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
