#!/usr/bin/env python3
"""
测试情感趋势修复脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保Django环境已初始化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
import django
django.setup()

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer
from datetime import datetime

if __name__ == "__main__":
    print("测试情感趋势修复...")
    print(f"当前日期: {datetime.now().date()}")
    
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 获取最近7天的情感趋势
    trend_data = analyzer.get_sentiment_trend(days=7)
    
    print("\n情感趋势数据:")
    for day in trend_data:
        print(f"日期: {day['date']}, 正面: {day['positive_count']}, 负面: {day['negative_count']}, 中性: {day['neutral_count']}, 平均得分: {day['avg_score']}")
    
    # 检查今天的日期是否包含在结果中
    today_str = datetime.now().date().strftime('%Y-%m-%d')
    today_data = next((day for day in trend_data if day['date'] == today_str), None)
    
    if today_data:
        print(f"\n✓ 成功: 包含今天({today_str})的数据")
        print(f"  今天数据: 正面{today_data['positive_count']}条, 负面{today_data['negative_count']}条, 中性{today_data['neutral_count']}条")
    else:
        print(f"\n✗ 失败: 不包含今天({today_str})的数据")
    
    # 检查是否连续7天的数据
    if len(trend_data) == 7:
        print("✓ 成功: 包含连续7天的数据")
    else:
        print(f"✗ 失败: 数据不完整，只有{len(trend_data)}天的数据")
    
    print("\n测试完成!")
