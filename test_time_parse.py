#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试时间解析功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.spiders.base_spider import BaseSpider
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_time_parse():
    """测试时间解析功能"""
    logger.info("开始测试时间解析功能...")
    
    # 创建BaseSpider的具体子类
    class TestSpider(BaseSpider):
        def crawl_news_list(self, page=1):
            pass
        
        def crawl_news_detail(self, news_url, basic_info):
            pass
    
    # 创建爬虫实例
    spider = TestSpider(platform_name='测试')
    
    # 测试用例，包括36氪常见的时间格式
    test_cases = [
        "1分钟前",
        "30分钟前",
        "2小时前",
        "12小时前",
        "1天前",
        "3天前",
        "昨天",
        "昨天 18:55",
        "前天",
        "前天 10:54",
        "2025-12-05 18:55",
        "2025-12-05 18:55:00",
        "2025-12-05",
        "12-05 18:55",
        "12-05",
        "2025/12/05 18:55:00",
        "2025/12/05",
        "12/05/2025 18:55:00",
        "12/05/2025",
        "18:55",
    ]
    
    for test_case in test_cases:
        try:
            result = spider.parse_datetime(test_case)
            logger.info(f"'{test_case}' -> {result}")
        except Exception as e:
            logger.error(f"解析失败 '{test_case}': {e}")
    
    logger.info("时间解析功能测试完成！")

if __name__ == "__main__":
    test_time_parse()
