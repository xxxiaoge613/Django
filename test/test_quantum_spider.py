#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的量子位爬虫
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.spiders.quantum_bit_spider import QuantumBitSpider
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_quantum_spider():
    """测试量子位爬虫"""
    logger.info("开始测试量子位爬虫...")
    
    # 创建爬虫实例
    spider = QuantumBitSpider()
    
    try:
        # 只爬取第一页，测试修复效果
        spider.crawl_news_list(page=1)
        logger.info("量子位爬虫测试完成！")
    except Exception as e:
        logger.error(f"量子位爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭爬虫资源
        spider.close()

if __name__ == "__main__":
    test_quantum_spider()
