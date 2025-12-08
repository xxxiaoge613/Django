from django.core.management.base import BaseCommand
from django.db import transaction
from news_analysis.models import News
from news_analysis.spiders.thirty_six_kr_spider import ThirtySixKrSpider
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """更新36kr新闻正文内容"""
    
    help = '更新数据库中现有36kr新闻的正文内容'
    
    def handle(self, *args, **options):
        """执行命令"""
        logger.info("开始更新36kr新闻正文内容...")
        
        # 获取所有36kr平台的新闻
        news_list = News.objects.filter(platform='36kr', is_valid=True, is_ad=False)
        total_count = news_list.count()
        logger.info(f"找到 {total_count} 条36kr新闻需要更新")
        
        # 创建爬虫实例
        spider = ThirtySixKrSpider()
        
        updated_count = 0
        failed_count = 0
        
        try:
            # 遍历所有新闻并更新
            for news in news_list[:10]:  # 先更新前10条测试
                logger.info(f"正在更新新闻: {news.title} (ID: {news.id})")
                try:
                    # 重新爬取新闻详情
                    # 由于crawl_news_detail方法会直接保存到数据库，我们需要修改它来支持更新
                    # 这里我们直接调用爬虫的方法，它会自动处理更新
                    basic_info = {
                        'title': news.title,
                        'publish_time': news.publish_time,
                        'author': news.author
                    }
                    
                    # 调用爬虫方法更新新闻
                    spider.crawl_news_detail(news.url, basic_info)
                    updated_count += 1
                    logger.info(f"成功更新新闻: {news.title}")
                except Exception as e:
                    logger.error(f"更新新闻失败: {news.title}, 错误: {e}")
                    failed_count += 1
                    continue
        finally:
            # 关闭爬虫资源
            spider.close()
        
        logger.info(f"36kr新闻更新完成！")
        logger.info(f"成功更新: {updated_count} 条")
        logger.info(f"更新失败: {failed_count} 条")
        logger.info(f"总共有: {total_count} 条36kr新闻")
        
        self.stdout.write(self.style.SUCCESS(f"成功更新 {updated_count} 条36kr新闻，失败 {failed_count} 条，总计 {total_count} 条"))
