#!/usr/bin/env python3
"""
微信公众号自动发布 v2 - 上传今日截图到草稿箱。

改进：
- 更健壮的登录检测
- 更好的页面导航逻辑
- 详细的调试信息
- 备用上传方案
"""
import asyncio
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
STATE_FILE = SCRIPT_DIR / "wechat_state.json"
BEIJING = timezone(timedelta(hours=8))


def today_str():
    return datetime.now(BEIJING).strftime("%Y-%m-%d")


def get_image_path():
    if len(sys.argv) >= 2:
        p = Path(sys.argv[1])
        if p.exists():
            return str(p)
        print(f"❌ 指定的图片不存在: {p}")
        sys.exit(1)
    img = PROJECT_DIR / "images" / f"{today_str()}.png"
    if img.exists():
        return str(img)
    print(f"❌ 未找到今日截图: {img}")
    print("   请先运行 screenshot.py 截图")
    sys.exit(1)


async def wait_for_login(page, browser, timeout=180):
    """等待用户扫码登录"""
    print("⚠️  需要扫码登录！请在浏览器中扫码...")
    print("   等待登录完成（最多3分钟）...")

    start = datetime.now()
    while (datetime.now() - start).seconds < timeout:
        current_url = page.url
        # 登录成功后会跳转到首页
        if "/cgi-bin/home" in current_url or "/cgi-bin/frame" in current_url:
            print(f"✅ 登录成功！URL: {current_url}")
            return True
        # 或者页面内容包含"首页"等字样
        try:
            content = await page.content()
            # 更严格的检测：必须同时有这些元素才算登录成功
            has_sidebar = "sidebar" in content.lower() or "menu" in content.lower()
            has_create = "新的创作" in content or "create" in content.lower()
            has_home = "首页" in content or "home" in content.lower()

            if has_sidebar and (has_create or has_home):
                print(f"✅ 检测到登录成功！(sidebar={has_sidebar}, create={has_create}, home={has_home})")
                # 打印 URL 信息
                print(f"   URL: {current_url}")
                # 尝试查找 iframe
                frames = page.frames
                if len(frames) > 1:
                    print(f"   检测到 {len(frames)} 个 iframe")
                    for i, frame in enumerate(frames):
                        print(f"     frame[{i}]: {frame.url[:60]}")
                return True
        except Exception:
            pass
        await page.wait_for_timeout(2000)

    print("❌ 登录超时")
    return False


async def navigate_to_draft(page, context):
    """导航到草稿编辑页面"""
    print("📝 导航到图文编辑...")

    # 方式1：尝试点击"新的创作"
    try:
        # 等待页面加载
        await page.wait_for_timeout(2000)

        # 查找"新的创作"按钮
        create_btn = page.locator('a:has-text("新的创作"), div:has-text("新的创作"), span:has-text("new-creation")')
        if await create_btn.count() > 0:
            print("   找到「新的创作」按钮，点击...")
            await create_btn.first.click(timeout=10000)
            await page.wait_for_timeout(2000)

            # 选择"图文消息"
            article_btn = page.locator('a:has-text("图文消息"), div:has-text("图文消息")')
            if await article_btn.count() > 0:
                await article_btn.first.click(timeout=5000)
                await page.wait_for_timeout(3000)
                return True
    except Exception as e:
        print(f"   ⚠️  菜单导航失败: {e}")

    # 方式2：直接访问编辑页面 URL
    print("   尝试直接访问编辑页面...")
    try:
        # 从当前 URL 提取 token
        token_match = re.search(r"token=(\d+)", page.url)
        if not token_match:
            content = await page.content()
            token_match = re.search(r"token['\"\s:=]+(\d+)", content)

        if token_match:
            token = token_match.group(1)
            edit_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=77&token={token}&lang=zh_CN"
            await page.goto(edit_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            print(f"   ✅ 已跳转到编辑页面")
            return True
    except Exception as e:
        print(f"   ⚠️  直接访问失败: {e}")

    # 方式3：从菜单进入
    print("   尝试从左侧菜单进入...")
    try:
        menu_items = await page.locator("a, div[class*='menu'], span").all()
        for item in menu_items[:50]:
            text = await item.text_content() or ""
            if "素材" in text or "图文" in text or "内容" in text:
                href = await item.get_attribute("href") or ""
                if "appmsg" in href or "material" in href:
                    await item.click(timeout=5000)
                    await page.wait_for_timeout(3000)
                    return True
    except Exception:
        pass

    return False


async def upload_image(page, context, image_path):
    """上传图片到编辑器"""
    print(f"🖼️  上传图片: {Path(image_path).name}")

    # 检查是否有新标签页（贴图页面）
    all_pages = context.pages
    tietu_page = None
    for p in all_pages:
        url = p.url
        if "tietu" in url or "material" in url:
            tietu_page = p
            break

    target = tietu_page if tietu_page else page
    print(f"   目标页面: {target.url[:60]}...")

    await target.wait_for_timeout(2000)

    # 方法1：查找图片添加按钮
    upload_success = False
    try:
        # 常见的图片添加按钮
        add_btns = [
            ".image-selector__add",
            ".js_add_img",
            ".weui-desktop-icon-btn",
            "[class*='add-image']",
            "[class*='addImage']",
            ".edui-default .edui-for-image",
        ]
        for selector in add_btns:
            btn = target.locator(selector).first
            if await btn.count() > 0:
                print(f"   找到添加按钮: {selector}")
                await btn.click(force=True, timeout=5000)
                await target.wait_for_timeout(1000)
                break
    except Exception as e:
        print(f"   ⚠️  添加按钮点击失败: {e}")

    # 方法2：查找并点击"本地上传"
    try:
        await target.evaluate("""() => {
            const elements = document.querySelectorAll('span, a, li, div');
            for (const el of elements) {
                const text = el.textContent || '';
                if (text.includes('本地上传') || text.includes('上传图片')) {
                    el.click();
                    return true;
                }
            }
            return false;
        }""")
        await target.wait_for_timeout(500)
    except Exception:
        pass

    # 方法3：直接设置 file input
    try:
        # 查找所有 file input
        file_inputs = target.locator("input[type=file]")
        count = await file_inputs.count()
        print(f"   找到 {count} 个 file input")

        for i in range(count):
            fi = file_inputs.nth(i)
            accept = await fi.get_attribute("accept") or ""
            name = await fi.get_attribute("name") or ""

            # 跳过缩略图 input
            if name == "file" and "image" not in accept:
                print(f"     input[{i}]: 跳过（缩略图）")
                continue

            is_visible = await fi.is_visible()
            print(f"     input[{i}]: name={name}, accept={accept[:30]}, visible={is_visible}")

            try:
                await fi.set_input_files(image_path)
                await target.evaluate(f"""() => {{
                    const inputs = document.querySelectorAll('input[type=file]');
                    if (inputs[{i}]) {{
                        inputs[{i}].dispatchEvent(new Event('change', {{bubbles: true}}));
                    }}
                }}""")
                upload_success = True
                print(f"   ✅ 上传成功（input[{i}]）")
                break
            except Exception as e:
                print(f"     ⚠️  设置失败: {e}")
                continue
    except Exception as e:
        print(f"   ⚠️  file input 查找失败: {e}")

    # 方法4：尝试通过页面 JavaScript 触发上传
    if not upload_success:
        try:
            print("   尝试 JavaScript 触发上传...")
            result = await target.evaluate("""() => {
                // 查找所有可能的上传触发器
                const uploaders = document.querySelectorAll(
                    '[data-upload], [class*="upload"], [id*="upload"], ' +
                    '.webuploader-container, .upload-btn'
                );
                return uploaders.length;
            }""")
            print(f"   找到 {result} 个上传触发器")
        except Exception:
            pass

    return upload_success


async def save_draft(page, context):
    """保存草稿"""
    print("💾 保存草稿...")

    # 检查是否有新标签页
    all_pages = context.pages
    target = all_pages[-1] if len(all_pages) > 1 else page

    try:
        save_btn = target.locator(
            'button:has-text("保存为草稿"), '
            'a:has-text("保存为草稿"), '
            'button:has-text("保存"), '
            '[class*="save"]'
        ).first

        if await save_btn.count() > 0:
            await save_btn.click(force=True, timeout=10000)
            await target.wait_for_timeout(2000)

            # 处理确认弹窗
            try:
                confirm = target.locator(
                    'button:has-text("确定"), '
                    'button:has-text("确认"), '
                    '.weui-dialog__btn_primary'
                ).first
                if await confirm.count() > 0:
                    await confirm.click(timeout=3000)
            except Exception:
                pass

            print("   ✅ 草稿保存成功！")
            return True
        else:
            print("   ⚠️  未找到保存按钮")
            return False
    except Exception as e:
        print(f"   ⚠️  保存失败: {e}")
        return False


async def main():
    image_path = get_image_path()
    print(f"📸 图片: {image_path}")
    print(f"⏰ 时间: {datetime.now(BEIJING).strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ 需要安装 playwright: pip install playwright && playwright install chromium")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        # 尝试复用登录状态
        storage_state = str(STATE_FILE) if STATE_FILE.exists() else None
        if storage_state:
            print("📂 尝试复用登录状态...")

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            storage_state=storage_state,
        )
        page = await context.new_page()

        # 打开微信公众号后台
        print("🌐 打开微信公众号后台...")
        await page.goto("https://mp.weixin.qq.com/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # 检查是否需要登录
        page_content = await page.content()
        is_login_page = "扫码" in page_content or "立即注册" in page_content

        if is_login_page:
            # 需要登录
            logged_in = await wait_for_login(page, browser)
            if not logged_in:
                await browser.close()
                sys.exit(1)

            # 登录成功后，等待页面跳转
            print("⏳ 等待页面跳转...")
            await page.wait_for_timeout(5000)
            print(f"📍 跳转后 URL: {page.url}")

            # 如果还是首页，尝试刷新
            if page.url == "https://mp.weixin.qq.com/":
                print("🔄 URL 未变，尝试刷新...")
                await page.reload(wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                print(f"📍 刷新后 URL: {page.url}")
        else:
            print("✅ 已登录（复用状态）")

        # 保存登录状态
        await context.storage_state(path=str(STATE_FILE))
        print(f"💾 登录状态已保存")

        # 导航到编辑页面
        print(f"\n📍 登录后当前 URL: {page.url}")
        await page.wait_for_timeout(3000)
        print(f"📍 等待后 URL: {page.url}")

        # 打印页面中的关键元素
        try:
            content = await page.content()
            print(f"📄 页面长度: {len(content)} 字符")

            # 查找包含关键词的部分
            keywords = ["新的创作", "图文消息", "素材管理", "草稿箱", "appmsg", "tuzhiguangli"]
            for kw in keywords:
                idx = content.find(kw)
                if idx >= 0:
                    snippet = content[max(0, idx-50):idx+100]
                    print(f"   🔍 '{kw}' 出现在: ...{snippet}...")

            elements_info = await page.evaluate("""() => {
                const info = [];
                // 查找所有可点击的菜单项
                const links = document.querySelectorAll('a, [onclick], [class*="menu"], [class*="nav"]');
                for (const el of links) {
                    const text = (el.textContent || '').trim().substring(0, 30);
                    const href = el.getAttribute('href') || '';
                    const cls = el.className || '';
                    if (text.length > 0 && text.length < 30) {
                        info.push({text, href: href.substring(0, 50), cls: cls.substring(0, 30)});
                    }
                }
                return info.slice(0, 20);
            }""")
            print(f"\n📋 页面元素 (共 {len(elements_info)} 个):")
            for e in elements_info[:15]:
                print(f"   - [{e.get('cls', '')[:20]}] {e.get('text', '')} -> {e.get('href', '')}")
        except Exception as e:
            print(f"⚠️  无法获取页面元素: {e}")

        nav_success = await navigate_to_draft(page, context)
        if not nav_success:
            print("❌ 无法导航到编辑页面")
            print("   请手动导航到「素材管理」→「新建图文」")
            input("   准备好后按 Enter 继续...")
        else:
            await page.wait_for_timeout(2000)

        # 上传图片
        upload_success = await upload_image(page, context, image_path)

        if upload_success:
            # 等待上传完成
            print("⏳ 等待上传完成...")
            await page.wait_for_timeout(5000)

            # 保存草稿
            await save_draft(page, context)
        else:
            print("\n⚠️  自动上传失败")
            print("   请手动上传图片并保存草稿")
            print(f"   图片路径: {image_path}")

        # 完成
        print(f"\n🎉 完成！")
        print(f"   请到公众号后台检查草稿箱")
        print(f"   确认无误后可手动发布")

        # 保持浏览器打开
        print("\n📌 浏览器保持打开，确认无误后关闭即可")
        try:
            await page.wait_for_event("close", timeout=300000)
        except Exception:
            pass

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
