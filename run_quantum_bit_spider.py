#!/usr/bin/env python3
"""
启动量子位爬虫脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保Django环境已初始化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
import django
django.setup()

from news_analysis.spiders.quantum_bit_spider import QuantumBitSpider
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('quantum_bit_spider.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("开始启动量子位爬虫")
        
        # 创建量子位爬虫实例
        quantum_bit_spider = QuantumBitSpider()
        
        try:
            # 运行爬虫，设置爬取页数（可根据需要调整）
            quantum_bit_spider.crawl_news_list(max_pages=5)
            logger.info("量子位爬虫启动成功并完成爬取")
        except KeyboardInterrupt:
            logger.info("用户中断了爬虫运行")
            quantum_bit_spider.close()
        
    except Exception as e:
        logger.error(f"启动量子位爬虫失败: {e}", exc_info=True)
        sys.exit(1)
