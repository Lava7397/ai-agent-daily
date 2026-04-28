#!/usr/bin/env python3
"""
AI Daily 翻译脚本（MyMemory API 版）
读取 daily_data.json → 为每条新闻添加 title_zh + summary_zh（中文翻译）
保留原始 title/summary 作为英文版本（规范化为 title_en / summary_en）。
"""
import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

BEIJING_TZ = timezone(timedelta(hours=8))

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "daily_data.json"

SECTION_KEYS = ("research", "github", "models", "community")

# MyMemory 翻译 API（免费，无需 key，每日限额 1000 词）
TRANSLATE_API = "https://api.mymemory.translated.net/get"
RATE_DELAY = 1.0  # 每次调用间隔，避免触发限流


def mymemory_translate(text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
    """调用 MyMemory 免费翻译 API"""
    if not text or len(text.strip()) < 3:
        return text

    # 清理：去除 markdown 标签、HTML 标签、多余空格
    clean = re.sub(r'【\w+】', '', text)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()

    if len(clean) < 3:
        return text

    try:
        resp = requests.get(
            TRANSLATE_API,
            params={"q": clean[:500], "langpair": f"{source_lang}|{target_lang}"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("responseStatus") == 200:
                translated = data["responseData"]["translatedText"]
                # 翻译可能丢失【来源】标记，尝试恢复
                if text.startswith("【"):
                    m = re.match(r'【(\w+)】', text)
                    if m:
                        return f"【{m.group(1)}】{translated}"
                return translated
    except Exception as e:
        print(f"  ⚠️ 翻译失败: {str(e)[:40]}")

    # API 失败回退：保留原文
    return text


def translate_item(item: dict) -> tuple[str, str]:
    """翻译单个条目，返回 (title_zh, summary_zh)"""
    title_en = (item.get("title") or "").strip()
    summary_en = (item.get("summary") or "").strip()

    # 标题翻译
    if title_en and not item.get("title_zh"):
        title_zh = mymemory_translate(title_en)
        item["title_zh"] = title_zh
    else:
        title_zh = item.get("title_zh", title_en)

    # 摘要翻译
    if summary_en and not item.get("summary_zh"):
        summary_zh = mymemory_translate(summary_en)
        item["summary_zh"] = summary_zh
    else:
        summary_zh = item.get("summary_zh", summary_en)

    # 规范化为 title_en / summary_en 字段
    if title_en and not item.get("title_en"):
        item["title_en"] = title_en
    if summary_en and not item.get("summary_en"):
        item["summary_en"] = summary_en

    return title_zh, summary_zh


def main():
    if not DATA_FILE.exists():
        print(f"❌ 未找到数据文件: {DATA_FILE}")
        return 1

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    print(f"📝 开始翻译 {sum(len(data.get(k, [])) for k in SECTION_KEYS)} 条新闻...")

    total_translated = 0
    for key in SECTION_KEYS:
        items = data.get(key, [])
        if not items:
            continue
        print(f"\n🔄 翻译板块 [{key}] ({len(items)} 条)")
        for i, item in enumerate(items, 1):
            title_zh, summary_zh = translate_item(item)
            total_translated += 1
            print(f"  [{i:2d}] {title_zh[:40]}...")
            time.sleep(RATE_DELAY)  # API 友好间隔

    # 备份原文件
    backup = DATA_FILE.with_suffix(".json.bak")
    if backup.exists():
        backup.unlink()
    DATA_FILE.rename(backup)
    print(f"\n✅ 已备份原文件: {backup.name}")

    # 写入翻译后数据
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8"
    )
    print(f"✅ 已写入: {DATA_FILE.name}  (共 {total_translated} 条)")

    # 打印样例
    print("\n=== 翻译样例 ===")
    for key in SECTION_KEYS:
        items = data.get(key, [])
        if items:
            item = items[0]
            print(f"\n[{key}] TOP 1:")
            print(f"  ZH title: {item.get('title_zh','')[:60]}")
            print(f"  EN title: {item.get('title_en','')[:60]}")
            print(f"  ZH summary: {item.get('summary_zh','')[:80]}...")

    return 0


if __name__ == "__main__":
    sys = __import__('sys')
    exit(main())
