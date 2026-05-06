#!/usr/bin/env python3
"""
AI Daily 翻译脚本（MyMemory API 版）
读取 daily_data.json → 为每条新闻添加 title_zh + summary_zh（中文翻译）
保留原始 title/summary 作为英文版本（规范化为 title_en / summary_en）。

翻译结果缓存在 .cache/translate-cache.json（按规范化文本 + 语言对做 sha256 key），
重复跑 translate.py 时命中缓存则不再请求 MyMemory。
"""
import hashlib
import json
import os
import re
import shutil
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

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
CACHE_DIR = BASE_DIR / ".cache"

SECTION_KEYS = ("research", "github", "models", "community")

# 会话内缓存（main 入口会预加载并在结束时落盘）
_TX_CACHE: dict[str, str] | None = None

# MyMemory 翻译 API（免费，无需 key，每日限额 1000 词）
TRANSLATE_API = "https://api.mymemory.translated.net/get"
RATE_DELAY = 1.0  # 每次调用间隔，避免触发限流
MAX_RETRIES = 3  # 失败重试次数


def _translate_cache_path() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / "translate-cache.json"


def _load_translate_cache() -> dict[str, str]:
    path = _translate_cache_path()
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            return {str(k): str(v) for k, v in obj.items()}
    except Exception:
        pass
    return {}


def _flush_translate_cache(store: dict[str, str]) -> None:
    path = _translate_cache_path()
    path.write_text(
        json.dumps(store, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _active_translate_cache() -> dict[str, str]:
    global _TX_CACHE
    if _TX_CACHE is None:
        _TX_CACHE = _load_translate_cache()
    return _TX_CACHE


def _norm_for_api(text: str) -> str:
    clean = re.sub(r"【\w+】", "", text)
    clean = re.sub(r"<[^>]+>", "", clean)
    return re.sub(r"\s+", " ", clean).strip()


def _cache_key(clean: str, source_lang: str, target_lang: str) -> str:
    blob = f"{source_lang}\x00{target_lang}\x00{clean}".encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _restore_bracket_prefix(original: str, translated: str) -> str:
    if original.startswith("【"):
        m = re.match(r"【(\w+)】", original)
        if m:
            return f"【{m.group(1)}】{translated}"
    return translated


def mymemory_translate(text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
    """调用 MyMemory 免费翻译 API，失败时重试并返回原文"""
    if not text or len(text.strip()) < 2:  # 降低阈值：<2 字符不翻译（如单个符号）
        return text

    clean = _norm_for_api(text)

    if len(clean) < 2:
        return text

    cache = _active_translate_cache()
    ck = _cache_key(clean, source_lang, target_lang)
    if ck in cache:
        return _restore_bracket_prefix(text, cache[ck])

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(
                TRANSLATE_API,
                params={"q": clean[:500], "langpair": f"{source_lang}|{target_lang}"},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("responseStatus") == 200:
                    translated = data["responseData"]["translatedText"]
                    cache[ck] = translated
                    return _restore_bracket_prefix(text, translated)
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
    global _TX_CACHE
    if not DATA_FILE.exists():
        print(f"❌ 未找到数据文件: {DATA_FILE}")
        return 1

    _TX_CACHE = _load_translate_cache()
    try:
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

        CACHE_DIR.mkdir(exist_ok=True)
        backup = CACHE_DIR / "daily_data.json.bak"
        if not backup.exists():
            shutil.copy(DATA_FILE, backup)
            print(f"✅ 已备份原文件: .cache/{backup.name}")
        else:
            print(f"✅ 备份已存在: .cache/{backup.name}")

        # 写回
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 已写入: {DATA_FILE}  (共 {total_translated} 条)")

        # 统计
        print("\n=== 翻译统计 ===")
        for key in SECTION_KEYS:
            items = data.get(key, [])
            zh_count = sum(
                1
                for it in items
                if it.get("title_zh") and it.get("title_zh") != it.get("title")
            )
            print(f"  {key}: {zh_count}/{len(items)} 条已翻译")

        return 0
    finally:
        if _TX_CACHE is not None:
            _flush_translate_cache(_TX_CACHE)


if __name__ == "__main__":
    import sys
    sys.exit(main())
