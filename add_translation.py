#!/usr/bin/env python3
"""为 daily_data.json 添加中文摘要（summary_zh）"""
import json
import os
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")

# 读取现有数据
hermes_dir = '/Users/lava/Hermes/ai-daily-h5'
data_path = os.path.join(hermes_dir, 'daily_data.json')

with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"当前日期: {data.get('date')}")
print(f"板块: {list(data.keys())}")

# 为每个板块添加中文摘要
def generate_zh_summary(item, section):
    """根据英文摘要生成中文摘要（80-150字）"""
    title_en = item.get('title', '')
    summary_en = item.get('summary', '')
    
    # 移除源标记前缀（【arXiv】等）
    clean_summary = summary_en
    if '】' in summary_en:
        clean_summary = summary_en.split('】', 1)[1].strip()
    
    # 基于标题和摘要生成中文提示
    prompt = f"将以下英文新闻摘要翻译成中文，要求：\n1. 80-150字\n2. 保留技术细节、数据、专有名词\n3. 语气专业客观\n\n标题：{title_en}\n摘要：{clean_summary}\n\n中文摘要："
    
    # 使用 Hermes Agent API 或 OpenAI 接口
    # 这里先用规则+关键词模拟，实际应该调用 LLM
    return translate_with_llm(title_en, clean_summary, section)

def translate_with_llm(title, summary_en, section):
    """调用 LLM 进行翻译（需要 API key）"""
    # 临时方案：使用简单的关键词替换+模板，实际需要真实的翻译 API
    # 由于无法直接调用外部 API，这里提供一个基于 template 的模拟
    
    # 对于已经含中文的 HN 社区，直接使用
    if section == 'community' and any('\u4e00' <= c <= '\u9fff' for c in summary_en):
        # 提取中文部分
        cn_parts = []
        for char in summary_en:
            if '\u4e00' <= char <= '\u9fff':
                cn_parts.append(char)
            else:
                break
        if len(cn_parts) > 5:
            existing_cn = ''.join(cn_parts)
            rest = summary_en[len(existing_cn):].strip()
            return f"【HN】{existing_cn} | {rest}"
    
    # 对于纯英文，返回需人工补充的标记
    # 实际应该调用 Claude/GPT API
    return f"【待翻译】{summary_en[:100]}..."

# 实际执行：使用 Hermes Agent 的 LLM 能力
print("\n=== 方案选择 ===")
print("1. 立即手动翻译（速度慢，质量可控）")
print("2. 调用 LLM API 自动翻译（需要 API key，速度快）")
print("3. 跳过，保留英文（不符合中英切换需求）")

choice = input("请选择方案 (1/2/3): ").strip()

if choice == "1":
    # 手动翻译模式：输出需要翻译的内容，人工处理后重新写入
    output = {}
    for section in ['research', 'github', 'models', 'community']:
        items = data.get(section, [])
        output[section] = []
        print(f"\n=== {section.upper()} 需要翻译的条目 ===")
        for i, item in enumerate(items, 1):
            title = item.get('title', '')
            summary = item.get('summary', '')
            print(f"\n{i}. {title}")
            print(f"   原文: {summary[:300]}")
            zh = input(f"   中文摘要(80-150字): ").strip()
            if zh:
                item['summary_zh'] = zh
            output[section].append(item)
    
    # 更新其他字段
    data['research'] = output['research']
    data['github'] = output['github']
    data['models'] = output['models']
    data['community'] = output['community']
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已更新 daily_data.json 添加中文摘要")
    
elif choice == "2":
    # 自动翻译：调用 API
    print("\n自动翻译需配置 API key，暂未实现")
    print("请使用方案1手动翻译，或后续补充 API 配置")
    
else:
    print("跳过翻译，保留英文")

print("\n完成！")
