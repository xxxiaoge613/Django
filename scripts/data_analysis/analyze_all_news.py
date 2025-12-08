#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为所有未分析的新闻执行情感分析
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_all_news():
    """为所有未分析的新闻执行情感分析"""
    logger.info("开始为所有未分析的新闻执行情感分析...")
    
    # 创建情感分析器实例
    analyzer = SentimentAnalyzer()
    
    # 执行情感分析
    result = analyzer.analyze_from_database()
    
    logger.info(f"情感分析完成！")
    logger.info(f"共分析 {result['analyzed_count']} 条新闻")
    logger.info(f"正面新闻: {result['positive_count']} 条")
    logger.info(f"负面新闻: {result['negative_count']} 条")
    logger.info(f"中性新闻: {result['neutral_count']} 条")
    
    return result

if __name__ == "__main__":
    analyze_all_news()
