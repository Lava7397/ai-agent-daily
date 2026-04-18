#!/usr/bin/env python3
"""
数据源探索器 - 自动发现新的 AI Agent 数据源。

探索途径：
1. 从现有文章的引用链接反向发现
2. 从 HN/Reddit 热门帖子中发现博客
3. 从 arXiv 热门论文的作者主页发现
4. 从 GitHub trending 项目的 README 中发现
"""
import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
REGISTRY_FILE = BASE_DIR / "sources_registry.json"
DATA_FILE = BASE_DIR / "daily_data.json"
BEIJING = timezone(timedelta(hours=8))


def load_registry():
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def save_registry(registry):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def load_daily_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def extract_domains_from_data(data):
    """从日报数据中提取所有引用的域名"""
    domains = Counter()
    for section in ("research", "github", "models", "community"):
        for item in data.get(section, []):
            url = item.get("url", "")
            if url:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    if domain and domain not in ("github.com", "arxiv.org", "twitter.com", "x.com"):
                        domains[domain] += 1
                except Exception:
                    pass
    return domains


def check_url_alive(url, timeout=10):
    """检查 URL 是否可访问"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def discover_from_references(data):
    """从日报数据的引用链接中发现新源"""
    candidates = []
    known_domains = set()

    # 获取已知域名
    registry = load_registry()
    for src in registry["sources"]:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(src["url"])
            known_domains.add(parsed.netloc.lower())
        except Exception:
            pass

    # 提取新域名
    domains = extract_domains_from_data(data)
    for domain, count in domains.most_common(20):
        if domain not in known_domains and count >= 1:
            candidates.append({
                "domain": domain,
                "source": "reference_analysis",
                "confidence": min(0.5 + count * 0.1, 0.9),
                "discovered_at": datetime.now(BEIJING).isoformat()
            })

    return candidates


def discover_from_hn_comments():
    """从 HN 评论中发现被推荐的博客/newsletter"""
    # TODO: 实现 HN API 调用，分析评论中的链接
    return []


def discover_from_arxiv_authors():
    """从 arXiv 热门论文的作者中发现个人主页"""
    # TODO: 实现 arXiv API 调用
    return []


def run_discovery():
    """运行完整的发现流程"""
    print("🔍 数据源探索器启动...")

    # 加载今日数据
    try:
        data = load_daily_data()
    except Exception as e:
        print(f"❌ 无法加载日报数据: {e}")
        return []

    # 1. 从引用链接发现
    print("📎 分析引用链接...")
    ref_candidates = discover_from_references(data)
    print(f"   发现 {len(ref_candidates)} 个候选域名")

    # 2. 合并去重
    all_candidates = ref_candidates

    # 3. 保存发现历史
    registry = load_registry()
    for candidate in all_candidates:
        registry["discovery_history"].append(candidate)

    # 只保留最近 100 条
    registry["discovery_history"] = registry["discovery_history"][-100:]
    save_registry(registry)

    print(f"\n📊 发现总结:")
    print(f"   新候选源: {len(all_candidates)}")
    print(f"   已注册源: {len(registry['sources'])}")

    if all_candidates:
        print("\n🌟 候选数据源:")
        for c in all_candidates[:10]:
            print(f"   - {c['domain']} (置信度: {c['confidence']:.2f})")

    return all_candidates


if __name__ == "__main__":
    run_discovery()
