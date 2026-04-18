#!/usr/bin/env python3
"""
数据源评估器 v2 - 基于实际使用效果评估。

评估维度：
- coverage: 今日是否贡献了内容 (0/1)
- volume: 贡献条目数占比
- quality: 贡献内容的平均质量（基于 tags、summary 长度）
- uniqueness: 是否提供了独特内容（不重复的域名）

综合评分 = historical_score * 0.4 + today_score * 0.6
"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).parent.parent
REGISTRY_FILE = BASE_DIR / "sources_registry.json"
DATA_FILE = BASE_DIR / "daily_data.json"
BEIJING = timezone(timedelta(hours=8))

# 已知来源域名映射
DOMAIN_TO_SOURCE = {
    "huggingface.co": "huggingface-papers",
    "github.com": "github-trending",
    "news.ycombinator.com": "hacker-news",
    "www.theverge.com": "the-verge-ai",
    "venturebeat.com": "venturebeat-ai",
    "arstechnica.com": "arstechnica-ai",
    "bensbites.beehiiv.com": "bens-bites",
    "www.anthropic.com": "anthropic-official",
    "twitter.com": "twitter-x",
    "x.com": "twitter-x",
    "polymarket.com": "polymarket",
    "openai.com": "openai-official",
}


def load_registry():
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def save_registry(registry):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def load_daily_data():
    with open(DATA_FILE) as f:
        return json.load(f)


def analyze_today():
    """分析今日数据的来源贡献"""
    data = load_daily_data()
    source_stats = {}

    for section in ("research", "github", "models", "community"):
        for item in data.get(section, []):
            url = item.get("url", "")
            if not url:
                continue

            domain = urlparse(url).netloc.lower()
            source_id = DOMAIN_TO_SOURCE.get(domain, f"unknown:{domain}")

            if source_id not in source_stats:
                source_stats[source_id] = {
                    "count": 0,
                    "sections": set(),
                    "has_tags": 0,
                    "avg_summary_len": 0,
                    "total_summary_len": 0
                }

            stats = source_stats[source_id]
            stats["count"] += 1
            stats["sections"].add(section)

            if item.get("tags"):
                stats["has_tags"] += 1

            summary_len = len(item.get("summary", ""))
            stats["total_summary_len"] += summary_len

    # 计算平均摘要长度
    for stats in source_stats.values():
        if stats["count"] > 0:
            stats["avg_summary_len"] = stats["total_summary_len"] / stats["count"]

    return source_stats, data


def calculate_today_score(stats, total_items):
    """计算今日表现分数"""
    if not stats or total_items == 0:
        return 0

    # 贡献度 (0-30分)
    contribution = min(stats["count"] / total_items * 100, 30)

    # 覆盖广度 (0-20分)
    coverage = min(len(stats["sections"]) * 5, 20)

    # 内容质量 (0-30分): 摘要长度 + tags 完整性
    avg_len = stats.get("avg_summary_len", 0)
    quality = min(avg_len / 150 * 20, 20)  # 150字满分
    if stats["count"] > 0:
        tag_ratio = stats["has_tags"] / stats["count"]
        quality += tag_ratio * 10

    # 独特性 (0-20分): 贡献越多越有价值
    uniqueness = min(stats["count"] * 5, 20)

    return contribution + coverage + quality + uniqueness


def run_evaluation():
    """运行评估"""
    print("📊 数据源评估器 v2 启动...\n")

    registry = load_registry()
    source_stats, data = analyze_today()
    total_items = sum(len(data.get(k, [])) for k in ("research", "github", "models", "community"))

    print(f"📅 日期: {data.get('date', 'unknown')}")
    print(f"📦 总条目: {total_items}")
    print(f"🔗 来源数: {len(source_stats)}\n")

    # 更新每个源的评分
    for source in registry["sources"]:
        source_id = source["id"]
        stats = source_stats.get(source_id)

        if stats:
            today_score = calculate_today_score(stats, total_items)
            historical = source.get("quality_score", 50)

            # 加权平均：今日表现占 60%，历史占 40%
            new_score = historical * 0.4 + today_score * 0.6
            source["quality_score"] = round(new_score, 1)
            source["last_evaluated"] = datetime.now(BEIJING).strftime("%Y-%m-%d")
            source["today_contributions"] = stats["count"]
            source["status"] = "active"

            print(f"✅ {source['name']}:")
            print(f"   今日贡献: {stats['count']} 条")
            print(f"   涉及板块: {', '.join(stats['sections'])}")
            print(f"   历史分: {historical:.1f} → 今日分: {today_score:.1f} → 综合: {source['quality_score']:.1f}")
        else:
            # 今日未使用，分数轻微衰减
            old_score = source.get("quality_score", 50)
            source["quality_score"] = round(old_score * 0.95, 1)
            source["today_contributions"] = 0
            print(f"⏭️  {source['name']}: 今日未使用 (分数衰减至 {source['quality_score']:.1f})")
        print()

    # 发现新来源
    for domain, stats in source_stats.items():
        if domain.startswith("unknown:"):
            real_domain = domain.replace("unknown:", "")
            print(f"🆕 发现未注册来源: {real_domain} ({stats['count']} 条)")

            # 添加到 discovery_history
            registry.setdefault("discovery_history", []).append({
                "domain": real_domain,
                "source": "usage_analysis",
                "contributions": stats["count"],
                "discovered_at": datetime.now(BEIJING).isoformat()
            })

    save_registry(registry)

    # 输出排名
    print("\n" + "=" * 50)
    print("🏆 数据源质量排名（基于实际使用效果）:")
    print("=" * 50)
    sorted_sources = sorted(registry["sources"], key=lambda s: s.get("quality_score", 0), reverse=True)
    for i, src in enumerate(sorted_sources, 1):
        score = src.get("quality_score", 0)
        today = src.get("today_contributions", 0)
        status = "✅" if src.get("status") == "active" else "⚠️"
        bar = "█" * int(score / 5)
        print(f"   {i}. {status} {src['name']:25s} {score:5.1f} {bar} (今日:{today})")


if __name__ == "__main__":
    run_evaluation()
