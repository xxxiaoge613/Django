#!/usr/bin/env python3
"""
测试关键词提取功能
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
from news_analysis.spiders.quantum_bit_spider import QuantumBitSpider
from news_analysis.views.visualization_views import get_hot_keywords

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_keyword_extraction():
    """测试关键词提取功能"""
    logger.info("开始测试关键词提取功能...")
    
    try:
        # 1. 测试直接调用关键词提取函数
        logger.info("1. 测试get_hot_keywords函数...")
        hot_keywords = get_hot_keywords(limit=10)
        logger.info(f"获取到热门关键词: {hot_keywords}")
        
        # 2. 测试从Keyword模型获取关键词
        logger.info("\n2. 测试从Keyword模型获取关键词...")
        keywords = Keyword.objects.all()[:10]
        logger.info(f"Keyword模型中共有 {Keyword.objects.count()} 个关键词")
        for keyword in keywords:
            logger.info(f"关键词: {keyword.keyword}, 新闻: {keyword.news.title[:30]}..., 权重: {keyword.weight}")
        
        # 3. 测试新闻保存时的自动关键词提取
        logger.info("\n3. 测试新闻保存时的自动关键词提取...")
        
        # 创建测试新闻数据
        test_news_data = {
            'title': '阿里巴巴2025财年Q3营收同比增长15%，云计算业务增速达30%',
            'content': '阿里巴巴集团今日发布2025财年第三季度财报，营收同比增长15%至3200亿元人民币。其中，云计算业务表现亮眼，增速达30%，成为集团增长的重要引擎。财报显示，阿里巴巴在人工智能、大数据等技术领域的投入持续增加，推动了各业务板块的数字化转型。分析师认为，阿里巴巴的多元化业务布局和技术创新能力将继续支撑其未来增长。',
            'publish_time': django.utils.timezone.now(),
            'url': 'https://test.example.com/alibaba-q3-report-2025',
            'platform': '量子位',
            'source_id': 'alibaba-q3-2025',
            'author': '测试作者',
            'read_count': 1000,
            'is_valid': True,
            'is_ad': False
        }
        
        # 保存新闻
        news, created = News.objects.get_or_create(
            url=test_news_data['url'],
            defaults=test_news_data
        )
        
        if created:
            logger.info(f"创建测试新闻: {news.title}")
            
            # 直接使用关键词提取工具
            from news_analysis.utils.keyword_extractor import extract_news_keywords
            extracted_keywords = extract_news_keywords(news, limit=10)
            
            logger.info(f"使用工具提取到 {len(extracted_keywords)} 个关键词")
            for keyword_info in extracted_keywords:
                logger.info(f"关键词: {keyword_info['keyword']}, 权重: {keyword_info['weight']}, 出现次数: {keyword_info['count']}")
            
            # 保存关键词到数据库
            for keyword_info in extracted_keywords:
                Keyword.objects.create(
                    news=news,
                    keyword=keyword_info['keyword'],
                    weight=keyword_info['weight']
                )
            
            # 检查是否保存成功
            news_keywords = Keyword.objects.filter(news=news)
            logger.info(f"保存到数据库的关键词: {[kw.keyword for kw in news_keywords]}")
        else:
            logger.info(f"测试新闻已存在: {news.title}")
            news_keywords = Keyword.objects.filter(news=news)
            logger.info(f"已提取的关键词: {[kw.keyword for kw in news_keywords]}")
        
        # 4. 再次测试get_hot_keywords函数
        logger.info("\n4. 再次测试get_hot_keywords函数...")
        hot_keywords = get_hot_keywords(limit=10)
        logger.info(f"更新后的热门关键词: {hot_keywords}")
        
        logger.info("\n✅ 关键词提取功能测试完成！")
        return True
    except Exception as e:
        logger.error(f"❌ 关键词提取功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_keyword_extraction()
    sys.exit(0 if success else 1)