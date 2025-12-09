from django.core.management.base import BaseCommand
from django.db import transaction
from news_analysis.models import News, PlatformChoice
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Django命令，用于清空36kr新闻数据"""
    
    help = '清空数据库中所有36kr平台的新闻数据及其关联数据'
    
    def handle(self, *args, **options):
        """命令处理函数"""
        self.stdout.write(self.style.WARNING('开始清空36kr新闻数据...'))
        
        try:
            with transaction.atomic():
                # 查询所有36kr的新闻
                kr_news = News.objects.filter(platform=PlatformChoice.THIRTY_SIX_KR)
                count = kr_news.count()
                
                if count == 0:
                    self.stdout.write(self.style.SUCCESS('数据库中没有36kr的新闻数据'))
                    return
                
                # 删除所有36kr的新闻（级联删除关联数据）
                kr_news.delete()
                
                self.stdout.write(self.style.SUCCESS(f'成功清空 {count} 条36kr新闻数据'))
                self.stdout.write(self.style.SUCCESS('关联的情感分析、评论、收藏、关键词等数据也已自动删除'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'清空36kr新闻数据失败: {str(e)}'))
            logger.error(f'清空36kr新闻数据命令执行失败: {e}')