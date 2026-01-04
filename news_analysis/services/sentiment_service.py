import logging
from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer as CoreSentimentAnalyzer
from news_analysis.repositories.news_repository import NewsRepository
from news_analysis.repositories.sentiment_repository import SentimentRepository

logger = logging.getLogger(__name__)

class SentimentService:
    """情感分析服务层，封装情感分析的业务逻辑"""
    
    def __init__(self):
        self.core_analyzer = CoreSentimentAnalyzer()
        self.news_repo = NewsRepository()
        self.sentiment_repo = SentimentRepository()
    
    def analyze_news_sentiment(self, news):
        """分析单篇新闻的情感"""
        return self.core_analyzer.analyze_news_sentiment(news)
    
    def analyze_text_sentiment(self, text):
        """分析文本的情感"""
        return self.core_analyzer.analyze_sentiment(text)
    
    def analyze_batch_news(self, news_list):
        """批量分析新闻情感"""
        return self.core_analyzer.analyze_batch_news(news_list)
    
    def analyze_from_database(self):
        """从数据库中读取新闻进行情感分析"""
        logger.info("开始从数据库中分析新闻情感")
        
        try:
            # 获取需要进行情感分析的新闻
            news_list = self.news_repo.get_news_for_sentiment_analysis()
            logger.info(f"找到 {news_list.count()} 条需要进行情感分析的新闻")
            
            analyzed_count = 0
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for news in news_list:
                # 分析新闻情感
                sentiment_result = self.analyze_news_sentiment(news)
                
                # 保存分析结果到数据库
                self.sentiment_repo.create_sentiment_analysis(
                    news=news,
                    sentiment_score=sentiment_result['sentiment_score'],
                    sentiment_type=sentiment_result['sentiment_type']
                )
                
                analyzed_count += 1
                
                # 统计情感类型
                if sentiment_result['sentiment_type'] == '正面':
                    positive_count += 1
                elif sentiment_result['sentiment_type'] == '负面':
                    negative_count += 1
                else:
                    neutral_count += 1
            
            logger.info(f"情感分析完成，共分析 {analyzed_count} 条新闻")
            logger.info(f"正面: {positive_count}, 负面: {negative_count}, 中性: {neutral_count}")
            
            return {
                'analyzed_count': analyzed_count,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count
            }
        except Exception as e:
            logger.error(f"从数据库中分析新闻情感失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'analyzed_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
    
    def get_sentiment_trend(self, days=7):
        """获取指定天数内的情感趋势"""
        return self.sentiment_repo.get_sentiment_trend(days=days)
    
    def get_sentiment_distribution(self):
        """获取整体情感分布"""
        from news_analysis.models import SentimentAnalysis
        
        try:
            total_count = SentimentAnalysis.objects.count()
            
            if total_count == 0:
                return {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'total': 0,
                    'positive_ratio': 0,
                    'negative_ratio': 0,
                    'neutral_ratio': 0
                }
            
            # 统计各情感类型数量
            positive_count = SentimentAnalysis.objects.filter(sentiment_type='正面').count()
            negative_count = SentimentAnalysis.objects.filter(sentiment_type='负面').count()
            neutral_count = SentimentAnalysis.objects.filter(sentiment_type='中性').count()
            
            return {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count,
                'total': total_count,
                'positive_ratio': round(positive_count / total_count * 100, 2),
                'negative_ratio': round(negative_count / total_count * 100, 2),
                'neutral_ratio': round(neutral_count / total_count * 100, 2)
            }
        except Exception as e:
            logger.error(f"获取情感分布失败: {e}")
            return {
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'total': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0
            }