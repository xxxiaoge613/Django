from django.db.models import Q, Count, F
from news_analysis.models import News
from datetime import datetime, timedelta

class NewsRepository:
    """新闻数据访问层，封装新闻相关的数据库操作"""
    
    @staticmethod
    def get_news_by_id(news_id, is_valid=True):
        """根据ID获取新闻"""
        return News.objects.get(id=news_id, is_valid=is_valid)
    
    @staticmethod
    def get_news_list(platform=None, sentiment=None, search_query=None, search_mode='keyword', page=1, page_size=10):
        """获取新闻列表，支持筛选和分页"""
        query = Q(is_valid=True)
        
        if platform:
            query &= Q(platform=platform)
        
        if sentiment:
            query &= Q(sentiment__sentiment_type=sentiment)
        
        if search_query:
            if search_mode == 'title':
                query &= Q(title__icontains=search_query)
            else:
                query &= (Q(title__icontains=search_query) | \
                         Q(content__icontains=search_query) | \
                         Q(keywords__keyword=search_query))
        
        news_list = News.objects.filter(query).distinct().order_by('-publish_time')
        
        return news_list
    
    @staticmethod
    def get_available_platforms():
        """获取所有可用的平台列表"""
        return list(set(News.objects.filter(is_valid=True).values_list('platform', flat=True)))
    
    @staticmethod
    def increase_read_count(news_id):
        """增加新闻阅读量"""
        news = News.objects.get(id=news_id)
        news.read_count += 1
        news.save()
        return news
    
    @staticmethod
    def get_related_news(news_id, limit=5):
        """获取相关推荐新闻"""
        news = News.objects.get(id=news_id)
        related_news = News.objects.filter(
            Q(platform=news.platform) & ~Q(id=news_id),
            is_valid=True
        ).order_by('-publish_time')[:limit]
        return related_news
    
    @staticmethod
    def get_hot_news(days=7, limit=10):
        """获取最近指定天数内热度最高的新闻"""
        from django.utils import timezone
        
        # 计算days天前的日期
        days_ago = timezone.now() - timedelta(days=days)
        
        # 查询最近days天的新闻，并计算热度
        hot_news = News.objects.filter(
            publish_time__gte=days_ago,
            is_valid=True
        ).annotate(
            # 计算评论数
            comment_count=Count('comments', filter=Q(comments__is_deleted=False)),
            # 计算收藏数
            collection_count=Count('collections'),
            # 讨论热度 = 评论数
            discussion_heat=F('comment_count'),
            # 传播热度 = 收藏数
            spread_heat=F('collection_count'),
            # 互动量 = 评论数 + 收藏数
            interaction=F('comment_count') + F('collection_count'),
            # 总曝光量 = 阅读量 + 1（避免除零）
            total_exposure=F('read_count') + 1,
            # 互动率 = 互动量 / 总曝光量
            interaction_rate=F('interaction') / F('total_exposure'),
            # 热度分数 = 阅读量（优先） + (讨论热度 + 传播热度) × 互动率
            hot_score=F('read_count') + (F('discussion_heat') + F('spread_heat')) * F('interaction_rate')
        ).order_by(
            '-hot_score'  # 按热度分数降序排序
        )[:limit]  # 取前10条
        
        return hot_news
    
    @staticmethod
    def get_news_for_sentiment_analysis():
        """获取需要进行情感分析的新闻列表"""
        return News.objects.filter(
            is_valid=True,
            sentiment__isnull=True
        )