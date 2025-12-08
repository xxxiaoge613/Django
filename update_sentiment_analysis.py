#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新新闻情感分析脚本
用于重新计算并更新数据库中所有新闻的情感分析结果
"""

import sys
import os
import logging

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django环境初始化
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject.settings")
django.setup()

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer
from news_analysis.models import News, SentimentAnalysis

def update_all_news_sentiment():
    """更新所有新闻的情感分析结果"""
    logger.info("开始更新所有新闻的情感分析结果")
    
    try:
        # 初始化情感分析器
        analyzer = SentimentAnalyzer()
        
        # 获取所有有效新闻
        all_news = News.objects.filter(is_valid=True, is_ad=False)
        total_count = all_news.count()
        
        logger.info(f"找到 {total_count} 条有效新闻")
        
        updated_count = 0
        
        for news in all_news:
            # 分析新闻情感
            sentiment_result = analyzer.analyze_news_sentiment(news)
            
            # 更新或创建情感分析结果
            sentiment, created = SentimentAnalysis.objects.update_or_create(
                news=news,
                defaults={
                    'sentiment_score': sentiment_result['sentiment_score'],
                    'sentiment_type': sentiment_result['sentiment_type']
                }
            )
            
            if created:
                logger.debug(f"为新闻 '{news.title}' 创建了新的情感分析结果")
            else:
                logger.debug(f"更新了新闻 '{news.title}' 的情感分析结果")
            
            updated_count += 1
            
            # 每处理50条新闻，记录一次进度
            if updated_count % 50 == 0:
                logger.info(f"已处理 {updated_count}/{total_count} 条新闻")
        
        logger.info(f"情感分析更新完成，共处理 {updated_count} 条新闻")
        
        # 统计更新后的情感分布
        sentiment_distribution = analyzer.get_sentiment_distribution()
        logger.info(f"更新后的情感分布：正面 {sentiment_distribution['positive']} 条，负面 {sentiment_distribution['negative']} 条，中性 {sentiment_distribution['neutral']} 条")
        
        return {
            'total_processed': updated_count,
            'distribution': sentiment_distribution
        }
        
    except Exception as e:
        logger.error(f"更新情感分析时出错: {e}", exc_info=True)
        raise

def update_pending_news_sentiment():
    """仅更新未进行情感分析的新闻"""
    logger.info("开始更新未进行情感分析的新闻")
    
    try:
        # 初始化情感分析器
        analyzer = SentimentAnalyzer()
        
        # 调用内置的分析方法
        result = analyzer.analyze_from_database()
        
        logger.info(f"更新完成，共分析 {result['analyzed_count']} 条新闻")
        logger.info(f"情感分布：正面 {result['positive_count']} 条，负面 {result['negative_count']} 条，中性 {result['neutral_count']} 条")
        
        return result
        
    except Exception as e:
        logger.error(f"更新未处理新闻情感分析时出错: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("======================================")
    logger.info("新闻情感分析更新脚本")
    logger.info("======================================")
    
    # 询问用户是更新所有新闻还是仅更新未处理的新闻
    import argparse
    
    parser = argparse.ArgumentParser(description='更新新闻情感分析结果')
    parser.add_argument('--all', action='store_true', help='更新所有新闻的情感分析结果')
    args = parser.parse_args()
    
    if args.all:
        logger.info("模式：更新所有新闻")
        update_all_news_sentiment()
    else:
        logger.info("模式：仅更新未进行情感分析的新闻")
        update_pending_news_sentiment()
    
    logger.info("======================================")
    logger.info("更新完成")
    logger.info("======================================")
