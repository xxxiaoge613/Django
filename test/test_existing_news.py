#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用优化后的情感分析模型测试现有新闻
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Django环境初始化
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from news_analysis.models import News
from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def test_existing_news():
    """
    使用优化后的情感分析模型测试现有新闻
    """
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 从数据库中读取所有新闻
    print("从数据库中读取所有新闻...")
    news_list = News.objects.filter(
        is_valid=True,
        is_ad=False
    ).order_by('-publish_time')
    
    print(f"\n共读取到{news_list.count()}条新闻\n")
    
    # 测试情感分析模型
    for i, news in enumerate(news_list, 1):
        print(f"样本 {i}:")
        print(f"标题: {news.title}")
        print(f"发布时间: {news.publish_time}")
        print(f"来源ID: {news.source_id}")
        
        # 进行情感分析
        sentiment_result = analyzer.analyze_news_sentiment(news)
        
        print(f"情感得分: {sentiment_result['sentiment_score']:.4f}")
        print(f"情感类型: {sentiment_result['sentiment_type']}")
        print(f"标题得分: {sentiment_result['title_score']:.4f}")
        print(f"内容得分: {sentiment_result['content_score']:.4f}")
        print("-" * 50)

if __name__ == "__main__":
    test_existing_news()
