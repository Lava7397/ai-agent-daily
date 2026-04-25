#!/usr/bin/env python3
"""
AI Agent 日报 — 截取部署页面生成分享图片
用 Playwright 打开 live 页面，html2canvas 截取渲染效果，保存到 images/
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "daily_data.json"
OUTPUT_DIR = BASE_DIR / "images"
LIVE_URL = os.environ.get("SITE_URL", "https://lava7397.com")


def get_date_str():
    data = json.loads(DATA_FILE.read_text())
    return data.get("date", datetime.now().strftime("%Y-%m-%d"))


async def main():
    from playwright.async_api import async_playwright

    date_str = get_date_str()
    output_path = OUTPUT_DIR / f"{date_str}.png"
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"📸 截取页面: {LIVE_URL.rstrip('/')}/today.html")
    print(f"📁 保存到: {output_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 720, "height": 800})
        page_url = f"{LIVE_URL.rstrip('/')}/today.html"
        await page.goto(page_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        # 用 html2canvas 截取（CDN 加载）
        data_url = await page.evaluate("""async () => {
            if (!window.html2canvas) {
                const s = document.createElement('script');
                s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
                document.head.appendChild(s);
                await new Promise(r => s.onload = r);
            }
            const canvas = await html2canvas(document.body, {
                scale: 2,
                windowWidth: 720,
                useCORS: true,
                backgroundColor: '#f5f0e8'
            });
            return canvas.toDataURL('image/png');
        }""")

        # 提取 base64 写入文件
        import base64
        b64_data = data_url.split(",")[1]
        img_bytes = base64.b64decode(b64_data)
        output_path.write_bytes(img_bytes)
        size_kb = len(img_bytes) / 1024
        print(f"✅ 已保存: {output_path} ({size_kb:.0f} KB)")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
