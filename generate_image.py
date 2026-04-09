#!/usr/bin/env python3
"""
AI Agent 日报 — 分享图片生成器
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

# --- 宫崎骏中性色调 (Ghibli-inspired neutral palette) ---
COLORS = {
    "bg_top":       (248, 245, 235),   # 暖白（天空留白）
    "bg_bottom":    (225, 232, 220),   # 淡草绿（吉卜力大地）
    "card":         (255, 253, 248),   # 暖白卡片
    "card_border":  (210, 205, 190),   # 温暖灰边框
    "card_shadow":  (230, 225, 215),   # 柔和阴影
    "header":       (75, 85, 70),      # 深草绿标题
    "section_text": (90, 85, 75),      # 暗褐板块标题
    "title":        (55, 50, 45),      # 正文标题
    "summary":      (110, 105, 95),    # 摘要文字
    "tag_bg":       (235, 240, 225),   # 标签背景（淡绿）
    "tag_text":     (100, 120, 80),    # 标签文字（草绿）
    "watermark":    (170, 165, 155),   # 水印
    "date_text":    (140, 135, 125),   # 日期
    "divider":      (225, 220, 210),   # 分隔线
    "accent1":      (180, 150, 110),   # 暖棕（研究）
    "accent2":      (100, 140, 120),   # 森林绿（GitHub）
    "accent3":      (140, 130, 170),   # 薰衣草紫（模型）
    "accent4":      (190, 140, 100),   # 琥珀色（社区）
    "ghibli_cloud": (255, 252, 245),   # 云朵白
    "ghibli_leaf":  (120, 155, 90),    # 叶子绿
    "ghibli_tuft":  (200, 195, 180),   # 草丛色
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

def draw_ghibli_cloud(draw, cx, cy, size=40, color=None):
    """绘制吉卜力风格的棉花糖云朵"""
    if color is None:
        color = COLORS["ghibli_cloud"]
    # 主体椭圆
    draw.ellipse([cx - size, cy - size * 0.5, cx + size, cy + size * 0.5], fill=color)
    # 左侧小圆
    draw.ellipse([cx - size * 0.7, cy - size * 0.8, cx - size * 0.1, cy - size * 0.1], fill=color)
    # 右侧小圆
    draw.ellipse([cx + size * 0.1, cy - size * 0.7, cx + size * 0.7, cy], fill=color)
    # 顶部小圆
    draw.ellipse([cx - size * 0.3, cy - size * 0.9, cx + size * 0.3, cy - size * 0.3], fill=color)


def draw_ghibli_leaf(draw, x, y, size=15, angle=0, color=None):
    """绘制吉卜力风格的小叶子"""
    if color is None:
        color = COLORS["ghibli_leaf"]
    # 简化的叶子形状（两个椭圆拼接）
    rad = math.radians(angle)
    for i in range(3):
        lx = x + int(i * size * 0.5 * math.cos(rad))
        ly = y + int(i * size * 0.5 * math.sin(rad))
        s = size - i * 2
        if s > 2:
            draw.ellipse([lx - s, ly - s // 2, lx + s, ly + s // 2], fill=color)


def draw_ghibli_grass_tuft(draw, x, y, width=60, color=None):
    """绘制吉卜力风格的小草丛"""
    if color is None:
        color = COLORS["ghibli_tuft"]
    for i in range(5):
        gx = x + i * (width // 5)
        gh = 8 + (i % 3) * 5
        draw.line([(gx, y), (gx - 2, y - gh)], fill=color, width=2)
        draw.line([(gx + 3, y), (gx + 5, y - gh + 2)], fill=COLORS["ghibli_leaf"], width=2)


def draw_ghibli_corner_decoration(draw, img_w, img_h, position="top-left"):
    """在边角绘制宫崎骏风格装饰（云朵 + 叶子 + 草丛）"""
    if position == "top-left":
        # 左上角：云朵 + 叶子
        draw_ghibli_cloud(draw, 120, 50, size=50)
        draw_ghibli_cloud(draw, 280, 35, size=30)
        draw_ghibli_leaf(draw, 60, 80, size=12, angle=-30)
        draw_ghibli_leaf(draw, 80, 95, size=10, angle=-15)
        draw_ghibli_leaf(draw, 45, 100, size=8, angle=10)
    elif position == "top-right":
        # 右上角：云朵 + 草丛
        draw_ghibli_cloud(draw, img_w - 150, 45, size=45)
        draw_ghibli_cloud(draw, img_w - 300, 30, size=25)
        draw_ghibli_leaf(draw, img_w - 50, 85, size=12, angle=210)
        draw_ghibli_leaf(draw, img_w - 70, 90, size=10, angle=195)
    elif position == "bottom-left":
        # 左下角：草丛 + 小叶子
        draw_ghibli_grass_tuft(draw, 30, img_h - 25, width=80)
        draw_ghibli_leaf(draw, 100, img_h - 40, size=10, angle=-45)
        draw_ghibli_cloud(draw, 180, img_h - 50, size=25, color=(245, 242, 235))
    elif position == "bottom-right":
        # 右下角：草丛 + 云朵
        draw_ghibli_grass_tuft(draw, img_w - 110, img_h - 25, width=80)
        draw_ghibli_leaf(draw, img_w - 120, img_h - 45, size=10, angle=225)
        draw_ghibli_cloud(draw, img_w - 200, img_h - 55, size=28, color=(245, 242, 235))


def draw_ghibli_header_decorations(draw, y_center):
    """在标题周围绘制宫崎骏风格小装饰"""
    # 左侧小星星（像吉卜力动画里的闪烁星光）
    star_positions = [(100, y_center - 10), (980, y_center + 5), (160, y_center + 20)]
    for sx, sy in star_positions:
        size = 4
        # 十字星光
        draw.line([(sx - size * 2, sy), (sx + size * 2, sy)], fill=COLORS["accent1"], width=1)
        draw.line([(sx, sy - size * 2), (sx, sy + size * 2)], fill=COLORS["accent1"], width=1)
        # 中心点
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=COLORS["accent1"])


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
    draw_ghibli_corner_decoration(draw, WIDTH, total_height, "top-left")
    draw_ghibli_corner_decoration(draw, WIDTH, total_height, "top-right")

    y = 0

    # ====== Header ======
    y += 50
    title = "AI Agent 日报"
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
    draw_ghibli_header_decorations(draw, y - 30)
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
        draw_ghibli_leaf(draw, decor_x, decor_y, size=8, angle=45, color=accent_color)
        draw_ghibli_leaf(draw, decor_x + 15, decor_y + 5, size=6, angle=60, color=accent_color)

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
    draw_ghibli_corner_decoration(draw, WIDTH, total_height, "bottom-left")
    draw_ghibli_corner_decoration(draw, WIDTH, total_height, "bottom-right")

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
