#!/usr/bin/env python3
"""
从 site-mascot-raw 导出站用图：裁边 → 等比缩放到长边 400~720 → 漫画风格（减色、略增饱和/对比、线稿感描边、USM 锐化），
生成 site-mascot.png 与 favicon / apple-touch。alpha 不变。
改素材时替换 images/site-mascot-raw.png 后运行本脚本即可。
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "images" / "site-mascot-raw.png"
OUT_PNG = BASE / "images" / "site-mascot.png"
OUT_ICO = BASE / "favicon.ico"
OUT_TOUCH = BASE / "apple-touch-icon.png"
MAX_W = 720
MIN_LONGE = 400
# 实色边：与四角色差低于此的像素视为「留白」
TRIM_BG_MAXDIFF = 12
# 漫画 / 平涂感：中值减少杂点、减色、FIND_EDGES 加粗线、沿边缘压暗
COMIC_MEDIAN_SIZE = 3
COMIC_COLOR_BOOST = 1.28
COMIC_CONTRAST_BOOST = 1.1
COMIC_LEVELS = 40  # 主色数，愈少愈「漫画」
COMIC_DITHER = False  # True 时略像印刷抖动，更柔
# 线稿感：0~1，0 为纯平涂无黑线
INK_LINE_STRENGTH = 0.3
# 反锐化（USM），在漫画处理最后做
SHARPEN_RADIUS = 0.5
SHARPEN_PERCENT = 105
SHARPEN_THRESHOLD = 2


def _sharpen_rgba(im: Image.Image) -> Image.Image:
    """仅对 RGB 做 UnsharpMask，不改动 A，避免白边/透明发灰。"""
    r, g, b, a = im.split()
    rgb = Image.merge("RGB", (r, g, b)).filter(
        ImageFilter.UnsharpMask(
            radius=SHARPEN_RADIUS, percent=SHARPEN_PERCENT, threshold=SHARPEN_THRESHOLD
        )
    )
    r2, g2, b2 = rgb.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def _comic_style_rgba(im: Image.Image) -> Image.Image:
    """高饱和/对比 + 中值去噪 + 减色分块 + 轻线稿，最后 USM。RGB 可改，A 原样接回。"""
    r, g, b, a = im.split()
    rgb = Image.merge("RGB", (r, g, b))
    if COMIC_MEDIAN_SIZE and COMIC_MEDIAN_SIZE > 0:
        try:
            rgb = rgb.filter(ImageFilter.MedianFilter(COMIC_MEDIAN_SIZE))
        except ValueError:
            pass
    rgb = ImageEnhance.Color(rgb).enhance(COMIC_COLOR_BOOST)
    rgb = ImageEnhance.Contrast(rgb).enhance(COMIC_CONTRAST_BOOST)

    dither = Image.Dither.ORDERED if COMIC_DITHER else Image.Dither.NONE
    try:
        p = rgb.quantize(
            colors=COMIC_LEVELS,
            method=Image.Quantize.MEDIANCUT,
            dither=dither,
        )
    except (AttributeError, TypeError, ValueError):
        p = rgb.quantize(COMIC_LEVELS, method=0, dither=0)
    out_rgb = p.convert("RGB")
    out = np.asarray(out_rgb, dtype=np.float32)

    if INK_LINE_STRENGTH > 0.001:
        edges = out_rgb.filter(ImageFilter.FIND_EDGES).convert("L")
        e = np.asarray(edges, dtype=np.float32) / 255.0
        e = np.clip((e - 0.03) * 1.25, 0.0, 1.0) ** 0.55
        factor = 1.0 - (INK_LINE_STRENGTH * 0.95 * e)
        factor = np.clip(factor[..., None], 0.2, 1.0)
        out = out * factor
        out = np.clip(out, 0.0, 255.0)

    fin = Image.fromarray(out.astype(np.uint8), "RGB")
    return _sharpen_rgba(Image.merge("RGBA", (*fin.split(), a)))


def _estimate_corner_background_rgb(arr: np.ndarray) -> np.ndarray:
    h, w, _ = arr.shape
    k = max(1, min(10, w // 15, h // 15))
    blocks = (
        arr[0:k, 0:k],
        arr[0:k, w - k : w],
        arr[h - k : h, 0:k],
        arr[h - k : h, w - k : w],
    )
    b = np.concatenate([x.reshape(-1, 4) for x in blocks], axis=0)
    return np.median(b[:, :3], axis=0).astype(np.float32)


def trim_screenshot_margins(im: Image.Image) -> Image.Image:
    """去透明外缘，再去与四角色接近的平铺留白。"""
    im = im.convert("RGBA")
    a = im.split()[-1]
    bb = a.getbbox()
    w0, h0 = im.size
    if bb is not None and bb != (0, 0, w0, h0):
        im = im.crop(bb)
    arr = np.asarray(im, dtype=np.uint8)
    if arr.size == 0:
        return im
    h, w = arr.shape[0], arr.shape[1]
    al = arr[:, :, 3].astype(np.int16)
    bg = _estimate_corner_background_rgb(arr)
    rgb = arr[:, :, :3].astype(np.float32)
    diff = np.max(np.abs(rgb - bg[None, None, :]), axis=2)
    mask = (al > 8) & (diff > TRIM_BG_MAXDIFF)
    if not np.any(mask):
        return im
    ys, xs = np.where(mask)
    top, left = int(ys.min()), int(xs.min())
    bottom, right = int(ys.max()) + 1, int(xs.max()) + 1
    return im.crop((left, top, right, bottom))


def _square_for_icon(im: Image.Image) -> Image.Image:
    w, h = im.size
    s = min(w, h)
    x, y = (w - s) // 2, (h - s) // 2
    return im.crop((x, y, x + s, y + s))


def build_main() -> Image.Image:
    im = trim_screenshot_margins(Image.open(RAW).convert("RGBA"))
    w, h = im.size
    longe = max(w, h)
    if longe < MIN_LONGE:
        sc = float(MIN_LONGE) / longe
    elif longe > MAX_W:
        sc = float(MAX_W) / longe
    else:
        sc = 1.0
    if sc < 0.999 or sc > 1.001:
        im = im.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS)
    return _comic_style_rgba(im)


def build_favicon_ico(hero: Image.Image) -> None:
    sq = _square_for_icon(hero)
    t180 = sq.resize((180, 180), Image.LANCZOS)
    t180.save(OUT_TOUCH, "PNG", optimize=True)
    a32 = sq.resize((32, 32), Image.LANCZOS)
    a48 = sq.resize((48, 48), Image.LANCZOS)
    a16 = sq.resize((16, 16), Image.LANCZOS)
    a32.save(OUT_ICO, format="ICO", sizes=[(48, 48), (32, 32), (16, 16)], append_images=[a48, a16])


def main() -> None:
    if not RAW.is_file():
        raise SystemExit(f"Missing {RAW}")
    main_img = build_main()
    main_img.save(OUT_PNG, "PNG", optimize=True)
    build_favicon_ico(main_img)
    print("OK", OUT_PNG, OUT_TOUCH, OUT_ICO, "size", main_img.size)


if __name__ == "__main__":
    main()
