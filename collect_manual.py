#!/usr/bin/env python3
"""
AI Daily - 手动采集脚本
从 7 个来源采集过去 48h 的 AI Agent 新闻，写入 daily_data.json
"""
import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.parse import quote_plus
import concurrent.futures

BEIJING_TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")

# 计算 48 小时前的时间点（用于 API 筛选）
SINCE_48H = datetime.now(BEIJING_TZ) - timedelta(hours=48)
# arXiv 用 5 天窗口（因为论文延迟）
ARXIV_SINCE = (datetime.now(BEIJING_TZ) - timedelta(days=5)).strftime("%Y-%m-%d")

def fetch_verge():
    """从 The Verge /ai 采集 - 使用 RSS"""
    url = "https://www.theverge.com/ai-artificial-intelligence/feed/"
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
        # 提取 RSS items
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        results = []
        for item in items[:5]:
            title_match = re.search(r'<title>(.*?)</title>', item)
            link_match = re.search(r'<link>(.*?)</link>', item)
            desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
            if title_match and link_match:
                # 清理 HTML 标签
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                summary = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()[:200] if desc_match else ""
                results.append({
                    "title": title,
                    "summary": f"【The Verge】{summary}",
                    "url": link_match.group(1),
                    "tags": ["industry", "policy"]
                })
        return results[:3]  # 最多 3 条
    except Exception as e:
        print(f"[WARN] Verge 采集失败: {e}")
        return []

def fetch_venturebeat():
    """从 VentureBeat /ai 采集 - 使用 RSS"""
    url = "https://venturebeat.com/category/ai/feed/"
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        results = []
        for item in items[:5]:
            title_match = re.search(r'<title>(.*?)</title>', item)
            link_match = re.search(r'<link>(.*?)</link>', item)
            desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
            if title_match and link_match:
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                summary = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()[:200] if desc_match else ""
                results.append({
                    "title": title,
                    "summary": f"【VentureBeat】{summary}",
                    "url": link_match.group(1),
                    "tags": ["enterprise", "funding"]
                })
        return results[:3]
    except Exception as e:
        print(f"[WARN] VentureBeat 采集失败: {e}")
        return []

def fetch_arstechnica():
    """从 Ars Technica /ai 采集 - 使用 RSS"""
    url = "https://feeds.arstechnica.com/arstechnica/technology-lab"
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        results = []
        for item in items[:5]:
            title_match = re.search(r'<title>(.*?)</title>', item)
            link_match = re.search(r'<link>(.*?)</link>', item)
            desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
            if title_match and link_match:
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                summary = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()[:200] if desc_match else ""
                results.append({
                    "title": title,
                    "summary": f"【Ars Technica】{summary}",
                    "url": link_match.group(1),
                    "tags": ["technical", "review"]
                })
        return results[:3]
    except Exception as e:
        print(f"[WARN] Ars Technica 采集失败: {e}")
        return []

def fetch_arxiv():
    """从 arXiv 采集论文 - API 查询"""
    base = "https://export.arxiv.org/api/query"
    # 多个子查询合并
    queries = [
        "ti:(AI+agent+OR+LLM+agent+OR+agentic+AI+OR+MCP)",
        "ti:(multi-agent+OR+tool+use+OR+function+calling)",
        "ti:(autonomous+agent+OR+agentic+workflow)"
    ]
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; AI-Daily-Bot/1.0)'}

    for q in queries:
        try:
            url = f"{base}?search_query={quote_plus(q)}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
            req = Request(url, headers=headers)
            with urlopen(req, timeout=20) as resp:
                content = resp.read().decode('utf-8')

            # 解析 entry
            entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)
            for entry in entries:
                title_match = re.search(r'<title>(.*?)</title>', entry)
                id_match = re.search(r'<id>(.*?)</id>', entry)
                summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                if title_match and id_match:
                    title = re.sub(r'\s+', ' ', title_match.group(1)).strip()
                    summary_raw = summary_match.group(1) if summary_match else ""
                    summary = re.sub(r'<[^>]+>', ' ', summary_raw).strip()[:250]

                    # 严格过滤：标题或摘要中必须包含 agent 相关关键词
                    combined = (title + " " + summary).lower()
                    if not any(kw in combined for kw in ['agent', 'llm', 'mcp', 'autonomous', 'tool use']):
                        continue

                    results.append({
                        "title": title,
                        "summary": f"【arXiv】{summary}",
                        "url": id_match.group(1),
                        "tags": ["research", "paper"]
                    })
        except Exception as e:
            print(f"[WARN] arXiv 查询失败 ({q}): {e}")

    # 去重 + 限制数量
    seen = set()
    unique = []
    for r in results:
        if r['title'] not in seen:
            seen.add(r['title'])
            unique.append(r)
    return unique[:4]

def fetch_github():
    """GitHub API 搜索 AI Agent 项目"""
    # 5 天窗口
    since_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    queries = [
        "ai+agent+language:python+stars:>100",
        "llm+agent+framework+language:python",
        "mcp+server+language:python",
        "claude+code+open+source"
    ]
    results = []
    headers = {'User-Agent': 'AI-Daily-Bot/1.0'}

    for q in queries:
        try:
            url = f"https://api.github.com/search/repositories?q={quote_plus(q)}+pushed:>={since_date}&sort=stars&order=desc&per_page=5"
            req = Request(url, headers=headers)
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            for item in data.get('items', [])[:3]:
                name = item['full_name']
                desc = (item['description'] or "")[:200]
                stars = item['stargazers_count']
                results.append({
                    "title": name,
                    "summary": f"【GitHub】{desc} （⭐ {stars}）",
                    "url": item['html_url'],
                    "stars": stars,
                    "tags": ["github", "opensource"]
                })
        except Exception as e:
            print(f"[WARN] GitHub 查询失败 ({q}): {e}")

    return results[:5]

def fetch_hackernews():
    """Hacker News Firebase API 获取热帖"""
    try:
        # 获取 top stories
        req = Request("https://hacker-news.firebaseio.com/v0/topstories.json", headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as resp:
            ids = json.loads(resp.read().decode('utf-8'))[:50]  # 前 50 条

        results = []
        keywords = ['ai', 'llm', 'agent', 'gpt', 'claude', 'model', 'mcp', 'langchain', 'openai', 'anthropic', 'agentic']

        def fetch_item(item_id):
            try:
                url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req, timeout=10) as resp:
                    item = json.loads(resp.read().decode('utf-8'))
                if not item or item.get('dead') or item.get('deleted'):
                    return None
                title = (item.get('title') or '').lower()
                if any(kw in title for kw in keywords):
                    return {
                        "title": item.get('title', ''),
                        "summary": f"【HN】热度: {item.get('score',0)} 分 | {item.get('descendants',0)} 评论",
                        "url": item.get('url', f"https://news.ycombinator.com/item?id={item_id}"),
                        "tags": ["community", "discussion"]
                    }
            except:
                return None
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(fetch_item, i) for i in ids]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res:
                    results.append(res)
                    if len(results) >= 6:
                        break
        return results[:6]
    except Exception as e:
        print(f"[WARN] Hacker News 采集失败: {e}")
        return []

def fetch_bensbites():
    """Ben's Bites - 尝试 RSS，失败则跳过"""
    # Ben's Bites 有付费墙，这里用 RSS 试一下
    url = "https://bensbites.beehiiv.com/feed"
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        results = []
        for item in items[:5]:
            title_match = re.search(r'<title>(.*?)</title>', item)
            link_match = re.search(r'<link>(.*?)</link>', item)
            if title_match and link_match:
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                results.append({
                    "title": title,
                    "summary": "【Ben's Bites】每日 AI 简报精选",
                    "url": link_match.group(1),
                    "tags": ["newsletter", "curation"]
                })
        return results[:3]
    except Exception as e:
        print(f"[WARN] Ben's Bites 无法访问（付费墙或RSS不可用），跳过: {e}")
        return []

# ========== 执行采集 ==========
print("=== AI Daily 数据采集开始 ===\n")

all_items = {
    "research": [],   # arXiv
    "github": [],     # GitHub
    "models": [],     # 新闻源归入 models
    "community": []   # HN
}

# 并发采集（除了 arxiv 和 github，其他也可以并发）
sources = [
    ("research", fetch_arstechnica),   # Ars -> research/models
    ("github", fetch_github),
    ("models", fetch_verge),
    ("models", fetch_venturebeat),
    ("models", fetch_bensbites),
    ("community", fetch_hackernews),
]

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    futures = {}
    for section, fn in sources:
        futures[executor.submit(fn)] = section

    for future in concurrent.futures.as_completed(futures):
        section = futures[future]
        try:
            items = future.result(timeout=30)
            all_items[section].extend(items)
            print(f"✓ {section}: 采集到 {len(items)} 条")
        except Exception as e:
            print(f"✗ {section} 失败: {e}")

# arXiv 单独处理
print("正在采集 arXiv...")
arxiv_items = fetch_arxiv()
all_items["research"] = arxiv_items[:4]  # 优先 arXiv
print(f"✓ research (arXiv): {len(arxiv_items)} 条")

# 统计
print(f"\n=== 采集汇总 ===")
total = 0
for section in ["research", "github", "models", "community"]:
    count = len(all_items[section])
    total += count
    print(f"  {section}: {count} 条")
print(f"  Total: {total} 条")

# 数量检查
if total < 18:
    print(f"\n⚠️  总条数不足（{total} < 18），需要补充数据")
    # 补充 GitHub
    if len(all_items["github"]) < 4:
        print("  补充 GitHub 项目...")
        extra_github = fetch_github()
        all_items["github"].extend(extra_github[:4-len(all_items["github"])])
    # 补充 community
    if len(all_items["community"]) < 5:
        print("  补充 HN 帖子...")
        extra_hn = fetch_hackernews()
        all_items["community"].extend(extra_hn[:5-len(all_items["community"])])
else:
    print(f"\n✓ 总条数达标：{total} 条")

# 截断每个板块到目标数量
all_items["research"] = all_items["research"][:4]
all_items["github"] = all_items["github"][:5]
all_items["models"] = all_items["models"][:4]
all_items["community"] = all_items["community"][:6]

# 构建 sources 字段 - 根据实际采集到的源
actual_sources = set()
# 添加已知成功的源
if any(item.get("summary", "").startswith("【Ars Technica】") for item in all_items["models"]):
    actual_sources.add("Ars Technica")
if any(item.get("summary", "").startswith("【VentureBeat】") for item in all_items["models"]):
    actual_sources.add("VentureBeat")
if any(item.get("summary", "").startswith("【The Verge】") for item in all_items["models"]):
    actual_sources.add("The Verge")
if any(item.get("summary", "").startswith("【Ben's Bites】") for item in all_items["models"]):
    actual_sources.add("Ben's Bites")
if any(item.get("summary", "").startswith("【HN】") for item in all_items["community"]):
    actual_sources.add("Hacker News")

# research 板块来源（arXiv）
if all_items["research"]:
    actual_sources.add("arXiv")

# github 板块来源
if all_items["github"]:
    actual_sources.add("GitHub")

# 按固定顺序排列
source_order = ["The Verge", "VentureBeat", "Ars Technica", "Ben's Bites", "Hacker News", "arXiv", "GitHub"]
sources_list = [s for s in source_order if s in actual_sources]
sources_str = ", ".join(sources_list)

# 构建 daily_data.json
output = {
    "date": TODAY,
    "sources": sources_str,
    "description": "AI Agent 领域最新情报",
    "research": [
        {
            "title": item["title"],
            "summary": item["summary"],
            "url": item["url"],
            "tags": item.get("tags", ["research"])
        }
        for item in all_items["research"]
    ],
    "github": [
        {
            "title": item["title"],
            "summary": item["summary"],
            "url": item["url"],
            "stars": item.get("stars", 0),
            "tags": item.get("tags", ["github"])
        }
        for item in all_items["github"]
    ],
    "models": [
        {
            "title": item["title"],
            "summary": item["summary"],
            "url": item["url"],
            "tags": item.get("tags", ["models"])
        }
        for item in all_items["models"]
    ],
    "community": [
        {
            "title": item["title"],
            "summary": item["summary"],
            "url": item["url"],
            "tags": item.get("tags", ["community"])
        }
        for item in all_items["community"]
    ]
}

# 写入文件
out_path = os.path.join(os.path.expanduser('~/Hermes/ai-daily-h5'), 'daily_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ daily_data.json 已写入: {out_path}")
print(f"   日期: {TODAY}")
print(f"   总条数: {sum(len(v) for v in all_items.values())}")
print(f"   sources: {sources_str}")
