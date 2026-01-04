from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

from news_analysis.services.sentiment_service import SentimentService
from news_analysis.services.visualization_service import VisualizationService

# 初始化服务
sentiment_service = SentimentService()
visualization_service = VisualizationService()

# 仪表盘视图
def dashboard(request):
    """可视化仪表盘视图"""
    try:
        # 获取情感趋势数据（最近7天）
        sentiment_trend = sentiment_service.get_sentiment_trend(days=7)
        
        # 获取情感分布数据
        sentiment_dist = sentiment_service.get_sentiment_distribution()
        
        # 获取平台分布数据
        platform_dist = visualization_service.get_platform_distribution()
        
        # 获取热门关键词数据
        hot_keywords = visualization_service.get_hot_keywords(limit=20)
        
        # 获取新闻统计数据
        news_stats = visualization_service.get_news_statistics()
        
        return render(request, 'visualization/dashboard.html', {
            'sentiment_trend': sentiment_trend,
            'sentiment_dist': sentiment_dist,
            'platform_dist': platform_dist,
            'hot_keywords': hot_keywords,
            'news_stats': news_stats
        })
    except Exception as e:
        logger.error(f"加载仪表盘失败: {e}")
        return render(request, 'visualization/dashboard.html', {
            'sentiment_trend': [],
            'sentiment_dist': {},
            'platform_dist': [],
            'hot_keywords': [],
            'news_stats': {}
        })

# 情感趋势视图
def sentiment_trend(request):
    """情感趋势视图"""
    days = int(request.GET.get('days', 7))
    trend_data = sentiment_service.get_sentiment_trend(days=days)
    
    return render(request, 'visualization/sentiment_trend.html', {
        'trend_data': trend_data,
        'days': days
    })

# 平台分布视图
def platform_distribution(request):
    """平台分布视图"""
    platform_data = visualization_service.get_platform_statistics()
    
    return render(request, 'visualization/platform_distribution.html', {
        'platform_data': platform_data
    })

# 关键词云视图
def keyword_cloud(request):
    """关键词云视图"""
    limit = int(request.GET.get('limit', 50))
    keywords = visualization_service.get_hot_keywords(limit=limit)
    
    return render(request, 'visualization/keyword_cloud.html', {
        'keywords': keywords,
        'limit': limit
    })


# 仪表盘数据JSON接口
def dashboard_data(request):
    """提供仪表盘JSON数据，用于前端实时更新"""
    try:
        # 获取情感趋势数据（最近7天）
        sentiment_trend = sentiment_service.get_sentiment_trend(days=7)
        
        # 获取情感分布数据
        sentiment_dist = sentiment_service.get_sentiment_distribution()
        
        # 获取平台分布数据
        platform_dist = visualization_service.get_platform_distribution()
        
        # 获取热门关键词数据
        hot_keywords = visualization_service.get_hot_keywords(limit=20)
        
        # 获取新闻统计数据
        news_stats = visualization_service.get_news_statistics()
        
        # 返回JSON数据
        return JsonResponse({
            'sentiment_trend': sentiment_trend,
            'sentiment_dist': sentiment_dist,
            'platform_dist': platform_dist,
            'hot_keywords': hot_keywords,
            'news_stats': news_stats
        })
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {e}")
        return JsonResponse({
            'sentiment_trend': [],
            'sentiment_dist': {},
            'platform_dist': {'dates': [], 'series': [], 'platforms': []},
            'hot_keywords': [],
            'news_stats': {}
        })
