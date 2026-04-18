#!/usr/bin/env python3
"""
数据源自我迭代系统 - 编排脚本

在每次日报生成后自动运行：
1. 分析今日数据，发现新候选源
2. 评估所有数据源质量
3. 输出优化建议

用法:
    python3 scripts/source_evolution.py
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
REGISTRY_FILE = BASE_DIR / "sources_registry.json"
BEIJING = timezone(timedelta(hours=8))


def load_registry():
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def analyze_daily_coverage():
    """分析今日数据的来源覆盖情况"""
    data_file = BASE_DIR / "daily_data.json"
    try:
        with open(data_file) as f:
            data = json.load(f)
    except Exception:
        return None

    sources_used = set()
    items_by_source = {}

    for section in ("research", "github", "models", "community"):
        for item in data.get(section, []):
            url = item.get("url", "")
            if url:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc.lower()
                sources_used.add(domain)
                items_by_source[domain] = items_by_source.get(domain, 0) + 1

    return {
        "date": data.get("date", "unknown"),
        "sources_used": list(sources_used),
        "items_by_source": items_by_source,
        "total_items": sum(len(data.get(k, [])) for k in ("research", "github", "models", "community"))
    }


def generate_suggestions(registry, coverage):
    """生成优化建议"""
    suggestions = []

    # 1. 检查是否有低质量源
    for src in registry["sources"]:
        if src.get("quality_score", 0) < 60:
            suggestions.append({
                "type": "warning",
                "message": f"⚠️  {src['name']} 质量评分偏低 ({src.get('quality_score', 0):.1f})，考虑替换"
            })

    # 2. 检查是否有未使用的高质量源
    if coverage:
        for src in registry["sources"]:
            try:
                from urllib.parse import urlparse
                domain = urlparse(src["url"]).netloc.lower()
                if domain not in coverage["sources_used"] and src.get("quality_score", 0) > 80:
                    suggestions.append({
                        "type": "info",
                        "message": f"💡 {src['name']} (评分 {src.get('quality_score', 0):.1f}) 今日未使用，可考虑增加采集"
                    })
            except Exception:
                pass

    # 3. 检查候选源
    recent_candidates = registry.get("discovery_history", [])[-5:]
    if recent_candidates:
        suggestions.append({
            "type": "opportunity",
            "message": f"🔍 发现 {len(recent_candidates)} 个新候选源待评估"
        })

    return suggestions


def run_evolution():
    """运行完整的迭代流程"""
    print("=" * 60)
    print("🧬 数据源自我迭代系统")
    print(f"⏰ {datetime.now(BEIJING).strftime('%Y-%m-%d %H:%M:%S')} 北京时间")
    print("=" * 60)

    # 1. 分析今日覆盖
    print("\n📊 Step 1: 分析今日数据覆盖...")
    coverage = analyze_daily_coverage()
    if coverage:
        print(f"   日期: {coverage['date']}")
        print(f"   总条目: {coverage['total_items']}")
        print(f"   来源数: {len(coverage['sources_used'])}")
        print(f"   来源: {', '.join(coverage['sources_used'][:5])}...")
    else:
        print("   ⚠️  无法加载今日数据")

    # 2. 运行探索器
    print("\n🔍 Step 2: 运行数据源探索...")
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from source_explorer import run_discovery
        candidates = run_discovery()
    except Exception as e:
        print(f"   ⚠️  探索器异常: {e}")
        candidates = []

    # 3. 运行评估器
    print("\n📊 Step 3: 运行数据源评估...")
    try:
        from source_evaluator import run_evaluation
        run_evaluation()
    except Exception as e:
        print(f"   ⚠️  评估器异常: {e}")

    # 4. 生成建议
    print("\n💡 Step 4: 生成优化建议...")
    registry = load_registry()
    suggestions = generate_suggestions(registry, coverage)

    if suggestions:
        for s in suggestions:
            print(f"   {s['message']}")
    else:
        print("   ✅ 当前配置良好，无需调整")

    # 5. 输出状态报告
    print("\n" + "=" * 60)
    print("📋 状态报告")
    print("=" * 60)
    print(f"已注册源: {len(registry['sources'])}")
    print(f"候选源:   {len(registry.get('discovery_history', []))}")
    print(f"今日覆盖: {len(coverage['sources_used']) if coverage else '?'} 个来源")

    # 质量排名
    sorted_sources = sorted(
        registry["sources"],
        key=lambda s: s.get("quality_score", 0),
        reverse=True
    )
    print("\n🏆 质量排名 Top 5:")
    for i, src in enumerate(sorted_sources[:5], 1):
        score = src.get("quality_score", 0)
        status = "✅" if src.get("status") == "active" else "⚠️"
        print(f"   {i}. {status} {src['name']}: {score:.1f}")

    print("\n✅ 迭代流程完成")
    return registry, suggestions


if __name__ == "__main__":
    run_evolution()
