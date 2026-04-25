#!/usr/bin/env python3
"""
为 images/ 下 PNG 做「高清」体积优化：
1) PNG：PIL 重新保存（optimize=True, compress_level=9），仅当更小时覆盖；
2) WebP：同内容导出为 .webp（quality 可调，默认 90，偏清晰；method=6 压缩更紧）。

改完吉祥物素材后可运行：python3 scripts/compress_images.py
依赖：Pillow（与 export_mascot_from_raw 一致）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent.parent
IMAGES = BASE / "images"


def optimize_png(path: Path) -> int:
    im = Image.open(path)
    if im.mode not in ("RGB", "RGBA", "P"):
        im = im.convert("RGBA" if "A" in im.mode else "RGB")
    tmp = path.with_suffix(".png.opt")
    im.save(tmp, format="PNG", optimize=True, compress_level=9)
    old, new = path.stat().st_size, tmp.stat().st_size
    if new < old:
        tmp.replace(path)
        return old - new
    tmp.unlink(missing_ok=True)
    return 0


def write_webp(png_path: Path, quality: int, method: int) -> Path:
    im = Image.open(png_path)
    if im.mode == "P" and "transparency" in im.info:
        im = im.convert("RGBA")
    out = png_path.with_suffix(".webp")
    im.save(
        out,
        format="WEBP",
        quality=quality,
        method=method,
    )
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument(
        "--quality",
        type=int,
        default=90,
        help="WebP 质量 1-100，默认 90（高清、体积仍明显小于 PNG）",
    )
    p.add_argument(
        "--method",
        type=int,
        default=6,
        choices=range(0, 7),
        help="WebP 编码 effort 0-6，默认 6 最省体积",
    )
    args = p.parse_args()

    if not IMAGES.is_dir():
        print(f"Missing: {IMAGES}", file=sys.stderr)
        return 1

    pngs = sorted(IMAGES.glob("*.png"))
    if not pngs:
        print("No PNG files in images/", file=sys.stderr)
        return 1

    total_png = 0
    for path in pngs:
        before = path.stat().st_size
        saved = optimize_png(path)
        after = path.stat().st_size
        total_png += saved
        webp = write_webp(path, quality=args.quality, method=args.method)
        wsz = webp.stat().st_size
        print(
            f"{path.name}: PNG {before} → {after} B (saved {saved} B) | WebP {wsz} B ({webp.name})"
        )

    print(f"Done. PNG total bytes saved: {total_png}. Update HTML to use <picture> + .webp when ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
