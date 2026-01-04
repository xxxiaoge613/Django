from news_analysis.models import SentimentAnalysis
from datetime import datetime, timedelta

class SentimentRepository:
    """情感分析数据访问层，封装情感分析相关的数据库操作"""
    
    @staticmethod
    def create_sentiment_analysis(news, sentiment_score, sentiment_type):
        """创建情感分析记录"""
        return SentimentAnalysis.objects.create(
            news=news,
            sentiment_score=sentiment_score,
            sentiment_type=sentiment_type
        )
    
    @staticmethod
    def get_sentiment_by_news_id(news_id):
        """根据新闻ID获取情感分析结果"""
        try:
            return SentimentAnalysis.objects.get(news_id=news_id)
        except SentimentAnalysis.DoesNotExist:
            return None
    
    @staticmethod
    def get_sentiment_trend(days=7):
        """获取指定天数内的情感趋势数据"""
        from django.utils.timezone import now
        
        # 获取当前日期（仅日期部分，不含时间）
        today = now().date()
        
        # 计算开始日期：days天前的日期
        start_date = today - timedelta(days=days-1)
        
        # 按日期分组统计情感趋势
        sentiment_trends = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            # 统计当天的新闻情感，确保包含整个日期范围（从零点到零点）
            sentiments = SentimentAnalysis.objects.filter(
                news__publish_time__date=current_date
            )
            
            if sentiments.exists():
                # 计算情感得分平均值
                avg_score = sum(s.sentiment_score for s in sentiments) / sentiments.count()
                
                # 统计各情感类型数量
                positive_count = sentiments.filter(sentiment_type='正面').count()
                negative_count = sentiments.filter(sentiment_type='负面').count()
                neutral_count = sentiments.filter(sentiment_type='中性').count()
                
                sentiment_trends.append({
                    'date': current_date.strftime('%m-%d'),
                    'avg_score': round(avg_score, 4),
                    'positive_count': positive_count,
                    'negative_count': negative_count,
                    'neutral_count': neutral_count,
                    'total_count': sentiments.count()
                })
            else:
                # 即使没有新闻，也要添加该日期的记录，保持图表连续
                sentiment_trends.append({
                    'date': current_date.strftime('%m-%d'),
                    'avg_score': 0.5,  # 默认中性得分
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_count': 0
                })
        
        return sentiment_trends