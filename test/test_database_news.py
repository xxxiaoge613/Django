#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试数据库中的新闻情感分析
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django环境初始化
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject.settings")
django.setup()

from news_analysis.models import News
from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def test_database_news():
    """直接测试数据库中的新闻情感分析"""
    print("=== 直接测试数据库中的新闻情感分析 ===")
    
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 获取数据库中的所有新闻
    all_news = News.objects.filter(is_valid=True, is_ad=False)[:20]  # 只测试前20条
    
    print(f"测试新闻数量: {len(all_news)}")
    
    # 统计结果
    negative_count = 0
    neutral_count = 0
    positive_count = 0
    
    for news in all_news:
        print(f"\n新闻标题: {news.title}")
        
        # 直接使用情感分析器分析
        result = analyzer.analyze_news_sentiment(news)
        
        print(f"情感得分: {result['sentiment_score']:.4f}")
        print(f"情感类型: {result['sentiment_type']}")
        print(f"标题得分: {result['title_score']:.4f}")
        print(f"内容得分: {result['content_score']:.4f}")
        
        # 检查是否是负面新闻
        if result['sentiment_type'] == '负面':
            negative_count += 1
        elif result['sentiment_type'] == '正面':
            positive_count += 1
        else:
            neutral_count += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"负面新闻: {negative_count}")
    print(f"中性新闻: {neutral_count}")
    print(f"正面新闻: {positive_count}")

if __name__ == "__main__":
    test_database_news()
