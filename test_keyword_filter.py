#!/usr/bin/env python3
"""
测试关键词过滤效果
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保Django环境已初始化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
import django
django.setup()

from news_analysis.utils.keyword_extractor import extract_keywords
from news_analysis.views.visualization_views import get_hot_keywords

# 测试文本，包含"具身"和"2025"等关键词
test_text = """
腾讯发布2025年人工智能战略，投资1000亿元发展AI基础设施。具身智能和生成式AI成为未来重点方向。
2025年将是AI发展的关键一年，具身化技术将推动机器人产业变革。
"""

print("=== 测试关键词过滤效果 ===")

# 1. 测试文本关键词提取
print("\n1. 测试文本关键词提取：")
keywords = extract_keywords(test_text, limit=15)
for i, keyword in enumerate(keywords, 1):
    print(f"{i}. {keyword['keyword']} - 权重: {keyword['weight']:.4f}, 出现次数: {keyword['count']}")

# 2. 测试热门关键词
print("\n2. 测试热门关键词：")
hot_keywords = get_hot_keywords(limit=20)
for i, keyword in enumerate(hot_keywords, 1):
    print(f"{i}. {keyword['keyword']} - 出现次数: {keyword['count']}")

# 3. 检查是否包含无意义关键词
print("\n3. 检查是否包含无意义关键词：")
target_keywords = ['具身', '具身化', '2025', '2024', '2023']
found = []
for keyword in hot_keywords:
    if keyword['keyword'] in target_keywords:
        found.append(keyword['keyword'])

if found:
    print(f"⚠️  警告：发现以下无意义关键词: {', '.join(found)}")
else:
    print("✅ 成功：未发现无意义关键词")
