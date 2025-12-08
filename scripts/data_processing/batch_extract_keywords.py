#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量提取关键词脚本
为所有未提取关键词的新闻重新提取并保存关键词
"""

import logging
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.models import News, Keyword
from news_analysis.utils.keyword_extractor import extract_news_keywords

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def batch_extract_keywords():
    """批量提取关键词"""
    logger.info("开始批量提取关键词...")
    
    # 获取所有有效新闻
    valid_news = News.objects.filter(is_valid=True, is_ad=False)
    total_news = valid_news.count()
    logger.info(f"共有 {total_news} 篇有效新闻")
    
    # 检查哪些新闻还没有提取关键词
    news_without_keywords = []
    news_with_keywords = []
    
    for news in valid_news:
        if not Keyword.objects.filter(news=news).exists():
            news_without_keywords.append(news)
        else:
            news_with_keywords.append(news)
    
    logger.info(f"已提取关键词的新闻: {len(news_with_keywords)} 篇")
    logger.info(f"未提取关键词的新闻: {len(news_without_keywords)} 篇")
    
    if not news_without_keywords:
        logger.info("所有新闻都已经提取了关键词，无需再处理")
        return
    
    # 为未提取关键词的新闻提取关键词
    logger.info(f"\n开始为 {len(news_without_keywords)} 篇新闻提取关键词...")
    
    processed_count = 0
    success_count = 0
    error_count = 0
    
    for i, news in enumerate(news_without_keywords, 1):
        logger.info(f"\n处理第 {i}/{len(news_without_keywords)} 篇新闻: {news.title}")
        
        try:
            processed_count += 1
            
            # 提取关键词
            extracted_keywords = extract_news_keywords(news, limit=10)
            
            if not extracted_keywords:
                logger.warning(f"未提取到关键词: {news.title}")
                continue
            
            # 保存关键词到数据库
            saved_keywords = []
            for keyword_info in extracted_keywords:
                keyword, created = Keyword.objects.get_or_create(
                    news=news,
                    keyword=keyword_info['keyword'],
                    defaults={'weight': keyword_info['weight']}
                )
                if created:
                    saved_keywords.append(keyword.keyword)
            
            if saved_keywords:
                logger.info(f"成功提取并保存 {len(saved_keywords)} 个关键词: {', '.join(saved_keywords[:5])}{'...' if len(saved_keywords) > 5 else ''}")
                success_count += 1
            else:
                logger.warning(f"所有关键词都已存在，未保存新关键词")
                
        except Exception as e:
            logger.error(f"处理新闻 {news.title} 时出错: {e}")
            error_count += 1
    
    logger.info(f"\n批量提取关键词完成！")
    logger.info(f"总处理新闻数: {processed_count}")
    logger.info(f"成功提取关键词的新闻: {success_count} 篇")
    logger.info(f"处理失败的新闻: {error_count} 篇")
    
    # 验证提取结果
    logger.info("\n验证提取结果...")
    total_keywords = Keyword.objects.count()
    logger.info(f"数据库中共有 {total_keywords} 个关键词")
    
    # 检查现在还有多少新闻没有关键词
    remaining_without_keywords = 0
    for news in valid_news:
        if not Keyword.objects.filter(news=news).exists():
            remaining_without_keywords += 1
    
    logger.info(f"现在还有 {remaining_without_keywords} 篇新闻没有提取关键词")
    
    if remaining_without_keywords == 0:
        logger.info("✅ 所有新闻都已成功提取关键词！")
    else:
        logger.info(f"❌ 仍有 {remaining_without_keywords} 篇新闻未提取关键词")

if __name__ == "__main__":
    batch_extract_keywords()