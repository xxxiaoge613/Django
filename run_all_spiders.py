#!/usr/bin/env python3
"""
启动所有新闻爬虫
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 确保Django环境已初始化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
import django
django.setup()

from news_analysis.spiders.spider_manager import SpiderManager
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('spider_run.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("开始启动所有爬虫")
        
        # 初始化爬虫管理器
        spider_manager = SpiderManager()
        
        # 运行所有爬虫
        spider_manager.run_all_spiders()
        
        logger.info("所有爬虫启动成功")
        
    except Exception as e:
        logger.error(f"启动爬虫失败: {e}", exc_info=True)
        sys.exit(1)
