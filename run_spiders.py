#!/usr/bin/env python
"""
独立运行爬虫的脚本
可以直接启动所有爬虫，无需通过Django管理命令
"""

import os
import sys
import django
import logging
from optparse import OptionParser

# 配置日志 - 设置为DEBUG级别，以便查看更详细的信息
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 设置Django环境变量并初始化Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject.settings")
django.setup()

# 导入模型和爬虫管理器
from news_analysis.models import News
from news_analysis.spiders.spider_manager import SpiderManager

def run_spiders(options):
    """运行爬虫"""
    logger.info("开始初始化爬虫管理器...")
    
    try:
        # 创建爬虫管理器
        spider_manager = SpiderManager()
        
        # 检查是否需要启动定时爬取
        if options.scheduled:
            interval = options.interval
            logger.info(f'启动定时爬取，间隔时间: {interval} 秒')
            spider_manager.start_scheduled_crawl(interval)
        else:
            # 运行前查看当前新闻数量
            before_count = News.objects.count()
            logger.info(f"运行前数据库中共有 {before_count} 条新闻")
            
            logger.info("开始运行单次爬取...")
            spider_manager.run_all_spiders()
            
            # 运行后查看新闻数量变化
            after_count = News.objects.count()
            new_count = after_count - before_count
            logger.info(f"运行后数据库中共有 {after_count} 条新闻，新增 {new_count} 条新闻")
            
            # 查看新增的新闻
            if new_count > 0:
                logger.info(f"\n新增的 {new_count} 条新闻：")
                latest_news = News.objects.order_by('-created_at')[:new_count]
                for news in latest_news:
                    logger.info(f"  - {news.platform} - {news.title[:50]}...")
            
            logger.info("所有爬虫运行完成！")
            
    except Exception as e:
        logger.error(f'爬虫运行失败: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    # 创建命令行参数解析器
    parser = OptionParser(usage="%prog [options]", description="运行新闻爬虫")
    
    # 添加命令行参数
    parser.add_option("-s", "--scheduled", action="store_true", dest="scheduled", 
                      default=False, help="启动定时爬取，默认间隔1小时")
    
    parser.add_option("-i", "--interval", type="int", dest="interval", 
                      default=3600, help="定时爬取间隔时间（秒），默认3600秒")
    
    # 解析命令行参数
    (options, args) = parser.parse_args()
    
    # 运行爬虫
    run_spiders(options)


if __name__ == "__main__":
    main()
