#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试关键词提取和保存功能
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

def test_keyword_save():
    """测试关键词提取和保存功能"""
    logger.info("开始测试关键词提取和保存功能...")
    
    try:
        # 创建新的测试新闻数据，使用唯一的URL
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        test_news_data = {
            'title': f'腾讯发布2025年人工智能战略，投资1000亿元发展AI基础设施 {unique_id}',
            'content': f'腾讯今日正式发布2025年人工智能战略，宣布将在未来三年投资1000亿元人民币，用于发展AI基础设施、人才培养和技术研发。腾讯CEO表示，人工智能是未来科技发展的核心驱动力，腾讯将加大在大模型、生成式AI、AI芯片等领域的投入。该战略包括建立全球最大的AI计算中心，培养10000名AI技术人才，以及推出一系列面向企业和消费者的AI产品。分析师认为，腾讯的AI战略将进一步巩固其在全球科技行业的地位，并推动整个AI产业的发展。 {unique_id}',
            'publish_time': django.utils.timezone.now(),
            'url': f'https://test.example.com/tencent-ai-strategy-2025-{unique_id}',
            'platform': '量子位',
            'source_id': f'tencent-ai-2025-{unique_id}',
            'author': '测试作者',
            'read_count': 2000,
            'is_valid': True,
            'is_ad': False
        }
        
        logger.info(f"创建测试新闻: {test_news_data['title']}")
        
        # 保存新闻到数据库
        news = News.objects.create(**test_news_data)
        logger.info(f"成功创建新闻，ID: {news.id}")
        
        # 测试关键词提取
        logger.info("\n1. 测试关键词提取...")
        extracted_keywords = extract_news_keywords(news, limit=10)
        
        logger.info(f"提取到 {len(extracted_keywords)} 个关键词:")
        for i, keyword_info in enumerate(extracted_keywords, 1):
            logger.info(f"{i}. {keyword_info['keyword']} - 权重: {keyword_info['weight']:.4f}, 出现次数: {keyword_info['count']}")
        
        # 测试关键词保存
        logger.info("\n2. 测试关键词保存到数据库...")
        saved_count = 0
        for keyword_info in extracted_keywords:
            keyword, created = Keyword.objects.get_or_create(
                news=news,
                keyword=keyword_info['keyword'],
                defaults={'weight': keyword_info['weight']}
            )
            if created:
                saved_count += 1
                logger.info(f"保存关键词: {keyword_info['keyword']}")
            else:
                logger.info(f"关键词已存在: {keyword_info['keyword']}")
        
        logger.info(f"\n✅ 成功保存 {saved_count} 个关键词到数据库")
        
        # 验证关键词是否正确保存
        logger.info("\n3. 验证关键词保存结果...")
        db_keywords = Keyword.objects.filter(news=news)
        logger.info(f"从数据库中检索到 {db_keywords.count()} 个关键词:")
        
        for i, keyword in enumerate(db_keywords, 1):
            logger.info(f"{i}. {keyword.keyword} - 权重: {keyword.weight:.4f}")
        
        # 验证关键词数量是否一致
        if len(extracted_keywords) == db_keywords.count():
            logger.info("\n✅ 关键词数量一致，保存成功！")
        else:
            logger.warning(f"\n⚠️ 关键词数量不一致: 提取 {len(extracted_keywords)} 个，保存 {db_keywords.count()} 个")
        
        # 测试从Keyword模型获取热门关键词
        logger.info("\n4. 测试从Keyword模型获取热门关键词...")
        from news_analysis.views.visualization_views import get_hot_keywords
        hot_keywords = get_hot_keywords(limit=15)
        
        logger.info(f"获取到 {len(hot_keywords)} 个热门关键词:")
        for i, keyword in enumerate(hot_keywords, 1):
            logger.info(f"{i}. {keyword['keyword']} - 出现次数: {keyword['count']}")
        
        # 检查测试关键词是否出现在热门关键词中
        test_keyword_found = False
        for keyword_info in extracted_keywords:
            if any(hk['keyword'] == keyword_info['keyword'] for hk in hot_keywords):
                test_keyword_found = True
                logger.info(f"\n✅ 测试关键词 '{keyword_info['keyword']}' 出现在热门关键词中")
                break
        
        if not test_keyword_found:
            logger.info("\n⚠️ 测试关键词未出现在热门关键词中（可能是因为数据量不足）")
        
        logger.info("\n✅ 关键词提取和保存功能测试完成！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试数据
        logger.info("\n清理测试数据...")
        # 保留测试数据以便手动验证
        # News.objects.filter(title__contains='腾讯发布2025年人工智能战略').delete()
        # logger.info("测试数据已清理")

if __name__ == "__main__":
    success = test_keyword_save()
    sys.exit(0 if success else 1)