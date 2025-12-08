#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试情感趋势函数是否包含今天的日期
"""

import os
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def test_sentiment_trend():
    """测试情感趋势函数"""
    print("开始测试情感趋势函数...")
    
    # 创建情感分析器实例
    analyzer = SentimentAnalyzer()
    
    # 获取7天的情感趋势
    trend_data = analyzer.get_sentiment_trend(days=7)
    
    print(f"\n获取到 {len(trend_data)} 天的情感趋势数据")
    print("\n日期列表：")
    for item in trend_data:
        print(f"- {item['date']}")
    
    # 检查是否包含今天的日期
    from django.utils.timezone import now
    today = now().strftime('%Y-%m-%d')
    today_in_data = any(item['date'] == today for item in trend_data)
    
    print(f"\n今天的日期：{today}")
    print(f"是否包含今天的日期：{'是' if today_in_data else '否'}")
    
    return today_in_data

if __name__ == "__main__":
    success = test_sentiment_trend()
    sys.exit(0 if success else 1)