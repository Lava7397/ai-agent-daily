#!/usr/bin/env python3
"""
WeChat Daily Push — 微信公众号自动发布
流程：登录 → 草稿箱 → 新的创作 → 贴图 → 上传图片 → 保存草稿
首次需扫码，后续自动复用会话。
"""
import asyncio
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATE_FILE = BASE_DIR / "scripts" / "wechat_state.json"
DATA_FILE = BASE_DIR / "daily_data.json"


def get_date_str():
    data = json.loads(DATA_FILE.read_text())
    return data.get("date", "")


def get_image_path():
    date_str = get_date_str()
    img = BASE_DIR / "images" / f"{date_str}.png"
    if img.exists():
        return str(img.resolve())
    imgs = sorted((BASE_DIR / "images").glob("*.png"), reverse=True)
    return str(imgs[0].resolve()) if imgs else None


async def main():
    from playwright.async_api import async_playwright

    image_path = get_image_path()
    if not image_path:
        print("❌ 未找到图片")
        return
    print(f"📸 图片: {image_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = (
            await browser.new_context(storage_state=json.loads(STATE_FILE.read_text()))
            if STATE_FILE.exists()
            else await browser.new_context()
        )
        page = await ctx.new_page()

        # 1) 登录
        await page.goto("https://mp.weixin.qq.com/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        if "login" in page.url:
            print("📱 请扫码登录...")
            await page.wait_for_url("**/cgi-bin/home**", timeout=120000)
            print("✅ 登录成功")
        STATE_FILE.write_text(json.dumps(await ctx.storage_state(), ensure_ascii=False))

        # 2) Token
        token = re.search(r"token=(\d+)", page.url).group(1)

        # 3) 草稿箱
        await page.goto(
            f"https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_card&type=77&token={token}&lang=zh_CN",
            wait_until="networkidle", timeout=30000,
        )
        await page.wait_for_timeout(2000)

        # 4) 加号 → 贴图（新标签）
        await page.locator(".weui-desktop__unfold-menu-opr-new").first.click(force=True, timeout=5000)
        await page.wait_for_timeout(2000)
        async with ctx.expect_page(timeout=10000) as np:
            await page.evaluate("""() => {
                for (const el of document.querySelectorAll('.new-creation__menu-item')) {
                    if (el.textContent.includes('贴图')) { el.click(); return; }
                }
            }""")
        tietu = await np.value
        await tietu.wait_for_load_state("networkidle", timeout=30000)
        await tietu.wait_for_timeout(5000)
        print("✅ 贴图页面")

        # 5) 上传图片
        # 5a. 点击图片区域展开上传菜单
        await tietu.locator(".image-selector__add").first.click(force=True, timeout=5000)
        await tietu.wait_for_timeout(1500)

        # 5b. 点击弹窗里的「本地上传」span
        await tietu.evaluate("""() => {
            const popup = document.querySelector('.pop-opr__list');
            if (!popup) return;
            const spans = popup.querySelectorAll('span');
            for (const s of spans) {
                if (s.textContent.includes('本地上传')) { s.click(); return; }
            }
        }""")
        await tietu.wait_for_timeout(1000)

        # 5c. 设置 file input
        fi = tietu.locator(".image-selector input[type=file], .js_upload_btn_container input[type=file]").first
        if await fi.count() > 0:
            await fi.set_input_files(image_path)
            await tietu.evaluate("""() => {
                const input = document.querySelector('.image-selector input[type=file], .js_upload_btn_container input[type=file]');
                if (input) input.dispatchEvent(new Event('change', {bubbles: true}));
            }""")
        print("📤 图片已上传")

        await tietu.wait_for_timeout(10000)

        # 6) 保存草稿
        print("💾 保存草稿...")
        await tietu.locator('button:has-text("保存为草稿")').first.click(force=True, timeout=5000)
        await tietu.wait_for_timeout(8000)

        await tietu.screenshot(path="/tmp/wechat_final.png")
        STATE_FILE.write_text(json.dumps(await ctx.storage_state(), ensure_ascii=False))
        await browser.close()
        print("✅ 完成 — 请到公众号后台草稿箱确认")


if __name__ == "__main__":
    asyncio.run(main())
