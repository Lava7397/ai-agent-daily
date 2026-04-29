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
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

BEIJING_TZ = timezone(timedelta(hours=8))

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "daily_data.json"

SECTION_KEYS = ("research", "github", "models", "community")

# MyMemory 翻译 API（免费，无需 key，每日限额 1000 词）
TRANSLATE_API = "https://api.mymemory.translated.net/get"
RATE_DELAY = 1.0  # 每次调用间隔，避免触发限流
MAX_RETRIES = 3  # 失败重试次数


def mymemory_translate(text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
    """调用 MyMemory 免费翻译 API，失败时重试并返回原文"""
    if not text or len(text.strip()) < 2:  # 降低阈值：<2 字符不翻译（如单个符号）
        return text

    # 清理：去除 markdown 标签、HTML 标签、多余空格
    clean = re.sub(r'【\w+】', '', text)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()

    if len(clean) < 2:
        return text

    for attempt in range(MAX_RETRIES):
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
                else:
                    # API 返回错误状态，重试
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RATE_DELAY * (attempt + 1))
                        continue
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RATE_DELAY * (attempt + 1))
                continue
            print(f"  ⚠️ 翻译失败 (重试{MAX_RETRIES}次后): {str(e)[:40]}")

    # 所有重试失败，回退到原文
    return text


def translate_item(item: dict) -> tuple[str, str]:
    """翻译单个条目，返回 (title_zh, summary_zh)"""
    title_en = (item.get("title") or "").strip()
    summary_en = (item.get("summary") or "").strip()

    # 标题翻译
    title_zh = item.get("title_zh", "").strip()
    if title_en and (not title_zh or title_zh == title_en or len(title_zh) < 2):
        # 特殊处理：识别语言，避免对中文内容调用 en->zh 翻译
        # 简单启发式：如果包含中文字符，说明原文已是中文
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in title_en)
        if has_chinese:
            title_zh = title_en  # 原文已是中文，直接使用
        else:
            # 尝试翻译
            translated = mymemory_translate(title_en)
            # 验证翻译是否有效（不是原文、长度有变化、或包含中文）
            if translated and translated != title_en and len(translated) > 1:
                title_zh = translated
            else:
                # 翻译失败/无效，保留原文
                title_zh = title_en
        item["title_zh"] = title_zh

    # 摘要翻译
    summary_zh = item.get("summary_zh", "").strip()
    if summary_en and (not summary_zh or summary_zh == summary_en or len(summary_zh) < 5):
        # 检测原文语言
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in summary_en)
        if has_chinese:
            summary_zh = summary_en  # 原文已是中文
        else:
            translated = mymemory_translate(summary_en)
            if translated and translated != summary_en and len(translated) > 5:
                summary_zh = translated
            else:
                summary_zh = summary_en
        item["summary_zh"] = summary_zh

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
    if not backup.exists():
        shutil.copy(DATA_FILE, backup)
        print(f"✅ 已备份原文件: {backup.name}")
    else:
        print(f"✅ 备份已存在: {backup.name}")

    # 写回
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 已写入: {DATA_FILE}  (共 {total_translated} 条)")

    # 统计
    print("\n=== 翻译统计 ===")
    for key in SECTION_KEYS:
        items = data.get(key, [])
        zh_count = sum(1 for it in items if it.get("title_zh") and it.get("title_zh") != it.get("title"))
        print(f"  {key}: {zh_count}/{len(items)} 条已翻译")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
