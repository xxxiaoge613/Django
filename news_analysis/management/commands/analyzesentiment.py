from django.core.management.base import BaseCommand
from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Django命令，用于分析新闻情感"""
    
    help = '分析新闻情感，基于SnowNLP模型和自定义财经情感词典'
    
    def handle(self, *args, **options):
        """命令处理函数"""
        self.stdout.write(self.style.SUCCESS('开始初始化情感分析器...'))
        
        try:
            # 创建情感分析器实例
            analyzer = SentimentAnalyzer()
            
            # 从数据库中分析新闻情感
            analysis_result = analyzer.analyze_from_database()
            
            # 输出分析结果
            self.stdout.write(self.style.SUCCESS(f'情感分析完成！'))
            self.stdout.write(self.style.SUCCESS(f'共分析 {analysis_result["analyzed_count"]} 条新闻'))
            self.stdout.write(self.style.SUCCESS(f'正面新闻: {analysis_result["positive_count"]} 条'))
            self.stdout.write(self.style.SUCCESS(f'负面新闻: {analysis_result["negative_count"]} 条'))
            self.stdout.write(self.style.SUCCESS(f'中性新闻: {analysis_result["neutral_count"]} 条'))
            
            # 计算情感分布比例
            total = analysis_result["analyzed_count"]
            if total > 0:
                self.stdout.write(self.style.SUCCESS('\n情感分布比例：'))
                self.stdout.write(self.style.SUCCESS(f'正面: {round(analysis_result["positive_count"]/total*100, 2)}%'))
                self.stdout.write(self.style.SUCCESS(f'负面: {round(analysis_result["negative_count"]/total*100, 2)}%'))
                self.stdout.write(self.style.SUCCESS(f'中性: {round(analysis_result["neutral_count"]/total*100, 2)}%'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'情感分析失败: {str(e)}'))
            logger.error(f'情感分析命令执行失败: {e}')
