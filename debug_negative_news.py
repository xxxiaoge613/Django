#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试负面新闻识别问题
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django环境初始化
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject.settings")
django.setup()

from news_analysis.models import News, SentimentAnalysis
from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def debug_negative_news():
    """调试负面新闻识别问题"""
    print("=== 调试负面新闻识别问题 ===")
    
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 获取所有有效新闻
    all_news = News.objects.filter(is_valid=True, is_ad=False)
    
    print(f"总新闻数: {all_news.count()}")
    
    # 查找包含明显负面关键词的新闻
    negative_keywords = [
        '下滑', '暴跌', '下降', '亏损', '失败', '风险', '危机',
        '诈骗', '造假', '调查', '处罚', '召回', '裁员', '离职',
        '压力', '问题', '受损', '断裂', '短缺', '恶化', '疲软',
        '低迷', '衰退', '萎缩', '失业', '违约', '债务', '坏账',
        '亏损', '破产', '负面', '挑战', '放缓', '停滞', '收缩'
    ]
    
    print(f"\n=== 查找包含明显负面关键词的新闻 ===")
    
    for news in all_news:
        # 检查标题是否包含负面关键词
        has_negative = False
        found_keywords = []
        
        for keyword in negative_keywords:
            if keyword in news.title:
                has_negative = True
                found_keywords.append(keyword)
        
        if has_negative:
            print(f"\n=====================================")
            print(f"ID: {news.id}")
            print(f"标题: {news.title}")
            print(f"包含的负面关键词: {', '.join(found_keywords)}")
            
            # 详细分析这条新闻
            title_result = analyzer.analyze_sentiment(news.title)
            content_result = analyzer.analyze_sentiment(news.content[:500])  # 只分析前500字
            
            print(f"\n标题情感分析:")
            print(f"  情感得分: {title_result['sentiment_score']:.4f}")
            print(f"  情感类型: {title_result['sentiment_type']}")
            print(f"  SnowNLP得分: {title_result['snow_score']:.4f}")
            print(f"  自定义词典得分: {title_result['financial_score']:.4f}")
            
            print(f"\n内容情感分析:")
            print(f"  情感得分: {content_result['sentiment_score']:.4f}")
            print(f"  情感类型: {content_result['sentiment_type']}")
            print(f"  SnowNLP得分: {content_result['snow_score']:.4f}")
            print(f"  自定义词典得分: {content_result['financial_score']:.4f}")
            
            # 查看新闻_analysis方法的结果
            news_result = analyzer.analyze_news_sentiment(news)
            print(f"\n新闻整体情感分析:")
            print(f"  情感得分: {news_result['sentiment_score']:.4f}")
            print(f"  情感类型: {news_result['sentiment_type']}")
            
            # 检查是否在数据库中已经有分析结果
            sentiment = SentimentAnalysis.objects.filter(news=news).first()
            if sentiment:
                print(f"\n数据库中的情感分析结果:")
                print(f"  情感得分: {sentiment.sentiment_score:.4f}")
                print(f"  情感类型: {sentiment.sentiment_type}")

if __name__ == "__main__":
    debug_negative_news()
