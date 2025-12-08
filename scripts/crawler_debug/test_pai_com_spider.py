#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商派爬虫测试脚本
"""

import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from news_analysis.spiders.pai_com_spider import PaiComSpider

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_pai_com_spider():
    """测试电商派爬虫"""
    try:
        logger.info("开始测试电商派爬虫")
        
        # 创建爬虫实例
        spider = PaiComSpider()
        
        try:
            # 爬取新闻列表
            spider.crawl_news_list()
            logger.info("电商派爬虫测试成功")
        except Exception as e:
            logger.error(f"电商派爬虫测试失败: {e}")
            raise
        finally:
            # 关闭爬虫资源
            spider.close()
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_pai_com_spider()
