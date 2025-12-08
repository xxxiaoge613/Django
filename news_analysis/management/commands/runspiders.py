from django.core.management.base import BaseCommand
from news_analysis.spiders.spider_manager import SpiderManager
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Django命令，用于运行爬虫"""
    
    help = '运行所有新闻爬虫，爬取财经新闻数据'
    
    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            '--scheduled',
            action='store_true',
            help='启动定时爬取，默认间隔1小时'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=3600,
            help='定时爬取间隔时间（秒），默认3600秒'
        )
        parser.add_argument(
            '--platform',
            type=str,
            help='只运行指定平台的爬虫（可选值：36kr, quantum_bit）'
        )
    
    def handle(self, *args, **options):
        """命令处理函数"""
        self.stdout.write(self.style.SUCCESS('开始初始化爬虫管理器...'))
        
        try:
            # 创建爬虫管理器
            spider_manager = SpiderManager()
            
            # 获取平台参数
            platform = options.get('platform')
            
            # 检查是否需要启动定时爬取
            if options['scheduled']:
                interval = options['interval']
                self.stdout.write(self.style.SUCCESS(f'启动定时爬取，间隔时间: {interval} 秒'))
                spider_manager.start_scheduled_crawl(interval)
            else:
                self.stdout.write(self.style.SUCCESS('开始运行单次爬取...'))
                if platform:
                    # 只运行指定平台的爬虫
                    for spider in spider_manager.spiders:
                        if spider.platform_name == platform:
                            self.stdout.write(self.style.SUCCESS(f'开始运行 {platform} 爬虫...'))
                            spider.crawl_news_list()
                            spider.close()
                            self.stdout.write(self.style.SUCCESS(f'{platform} 爬虫运行完成！'))
                            break
                    else:
                        self.stdout.write(self.style.ERROR(f'未找到指定平台的爬虫: {platform}'))
                else:
                    # 运行所有爬虫
                    spider_manager.run_all_spiders()
                self.stdout.write(self.style.SUCCESS('所有爬虫运行完成！'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'爬虫运行失败: {str(e)}'))
            logger.error(f'爬虫命令执行失败: {e}')
