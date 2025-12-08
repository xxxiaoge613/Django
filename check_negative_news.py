#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中是否存在负面新闻的脚本
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

def check_news_sentiment():
    """检查数据库中新闻的情感"""
    print("=== 检查数据库中新闻的情感 ===")
    
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 获取所有有效新闻
    all_news = News.objects.filter(is_valid=True, is_ad=False)[:50]  # 只检查前50条
    
    print(f"检查 {len(all_news)} 条新闻")
    print("=" * 50)
    
    # 统计结果
    negative_news_count = 0
    
    for news in all_news:
        # 分析新闻情感
        title = news.title
        content = news.content
        
        # 只分析标题，内容可能太长
        sentiment_result = analyzer.analyze_sentiment(title)
        sentiment_score = sentiment_result['sentiment_score']
        sentiment_type = sentiment_result['sentiment_type']
        
        print(f"标题: {title}")
        print(f"情感得分: {sentiment_score:.4f}")
        print(f"情感类型: {sentiment_type}")
        print("-" * 50)
        
        # 检查是否可能是负面新闻
        if any(keyword in title for keyword in [
            '下滑', '暴跌', '下降', '风险', '危机', '失败', '受损',
            '负面', '问题', '召回', '造假', '调查', '处罚', '违约',
            '裁员', '失业', '亏损', '破产', '压力', '挑战', '放缓'
        ]):
            print(f"⚠️  可能的负面新闻: {title}")
            print(f"   但模型识别为: {sentiment_type} (得分: {sentiment_score:.4f})")
            print("-" * 50)
            negative_news_count += 1
    
    print(f"找到 {negative_news_count} 条可能的负面新闻")

if __name__ == "__main__":
    check_news_sentiment()
