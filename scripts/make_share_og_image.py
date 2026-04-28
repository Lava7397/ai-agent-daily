#!/usr/bin/env python3
"""
从 site-mascot-raw.png 生成分享/OG 用小图：限制长边 + JPEG（通用预览）+ WebP（更省体积）。
依赖：Pillow
用法：python3 scripts/make_share_og_image.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "images" / "site-mascot-raw.png"
OUT_JPG = BASE / "images" / "site-mascot-og.jpg"
OUT_WEBP = BASE / "images" / "site-mascot-og.webp"
MAX_SIDE = 640
JPEG_QUALITY = 88
WEBP_QUALITY = 86
WEBP_METHOD = 6


def main() -> int:
    if not SRC.is_file():
        print(f"Missing source: {SRC}", file=sys.stderr)
        return 1
    im = Image.open(SRC)
    if im.mode in ("RGBA", "P"):
        if im.mode == "P" and "transparency" in im.info:
            im = im.convert("RGBA")
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[3])
            im = bg
        else:
            im = im.convert("RGB")
    else:
        im = im.convert("RGB")
    w, h = im.size
    m = max(w, h)
    if m > MAX_SIDE:
        scale = MAX_SIDE / m
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    im.save(OUT_JPG, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    im.save(
        OUT_WEBP,
        format="WEBP",
        quality=WEBP_QUALITY,
        method=WEBP_METHOD,
    )
    print(f"Wrote {OUT_JPG.name} ({OUT_JPG.stat().st_size} bytes)")
    print(f"Wrote {OUT_WEBP.name} ({OUT_WEBP.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
