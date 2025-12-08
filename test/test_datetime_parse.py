#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试日期时间解析功能
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

def test_datetime_parse():
    """测试日期时间解析功能"""
    logger.info("开始测试日期时间解析功能...")
    
    # 创建BaseSpider实例
    spider = BaseSpider("测试平台")
    
    # 测试用例
    test_cases = [
        "昨天 11:53",
        "前天 22:14",
        "前天 22:03",
        "昨天 11:48",
        "昨天 11:46",
        "昨天 11:42",
        "昨天 09:08",
        "3天前",
        "2小时前",
        "45分钟前",
        "2025-12-03",
        "2025-12-03 12:00",
        "",
        None
    ]
    
    for test_case in test_cases:
        try:
            result = spider.parse_datetime(test_case)
            logger.info(f"输入: '{test_case}' -> 输出: {result}")
        except Exception as e:
            logger.error(f"测试用例 '{test_case}' 失败: {e}")
    
    logger.info("日期时间解析测试完成！")

if __name__ == "__main__":
    test_datetime_parse()
