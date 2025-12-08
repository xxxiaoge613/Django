from django.core.management.base import BaseCommand
from news_analysis.data_cleaning.cleaner import DataCleaner
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Django命令，用于清洗新闻数据"""
    
    help = '清洗新闻数据，包括缺失值填充、广告识别和数据标准化'
    
    def handle(self, *args, **options):
        """命令处理函数"""
        self.stdout.write(self.style.SUCCESS('开始初始化数据清洗器...'))
        
        try:
            # 创建数据清洗器实例
            cleaner = DataCleaner()
            
            # 从数据库中清洗新闻数据
            cleaned_count, ad_count = cleaner.clean_from_database()
            
            # 生成数据质量报告
            quality_report = cleaner.get_data_quality_report()
            
            # 输出清洗结果
            self.stdout.write(self.style.SUCCESS(f'数据清洗完成！'))
            self.stdout.write(self.style.SUCCESS(f'共清洗 {cleaned_count} 条新闻'))
            self.stdout.write(self.style.SUCCESS(f'识别 {ad_count} 条广告新闻'))
            
            self.stdout.write(self.style.SUCCESS('\n数据质量报告：'))
            self.stdout.write(self.style.SUCCESS(f'总新闻数: {quality_report.get("total_news", 0)}'))
            self.stdout.write(self.style.SUCCESS(f'有效新闻数: {quality_report.get("valid_news", 0)}'))
            self.stdout.write(self.style.SUCCESS(f'广告新闻数: {quality_report.get("ad_news", 0)}'))
            self.stdout.write(self.style.SUCCESS(f'有效率: {quality_report.get("valid_rate", 0)}%'))
            self.stdout.write(self.style.SUCCESS(f'广告率: {quality_report.get("ad_rate", 0)}%'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'数据清洗失败: {str(e)}'))
            logger.error(f'数据清洗命令执行失败: {e}')
