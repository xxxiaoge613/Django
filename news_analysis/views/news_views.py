from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from news_analysis.services.news_service import NewsService
from news_analysis.services.sentiment_service import SentimentService
from news_analysis.services.visualization_service import VisualizationService

# 初始化服务
news_service = NewsService()
sentiment_service = SentimentService()
visualization_service = VisualizationService()

# 新闻列表视图
def news_list(request):
    """新闻列表视图"""
    # 获取筛选条件
    platform = request.GET.get('platform', '')
    sentiment = request.GET.get('sentiment', '')
    search_query = request.GET.get('q', '')
    search_mode = request.GET.get('search_mode', 'keyword')  # 'keyword'或'title'
    page = request.GET.get('page', 1)
    
    # 使用服务层获取新闻列表
    result = news_service.get_news_list(
        platform=platform,
        sentiment=sentiment,
        search_query=search_query,
        search_mode=search_mode,
        page=page
    )
    
    # 分页处理
    paginator = Paginator(result['news_list'], 10)
    page = request.GET.get('page', 1)
    
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    
    return render(request, 'news/news_list.html', {
        'news': news,
        'platforms': result['available_platforms'],
        'selected_platform': platform,
        'selected_sentiment': sentiment,
        'search_query': search_query,
        'search_mode': search_mode
    })

# 新闻详情视图
def news_detail(request, pk):
    """新闻详情视图"""
    # 使用服务层获取新闻详情
    result = news_service.get_news_detail(pk, request.user)
    
    return render(request, 'news/news_detail.html', result)

# 新闻搜索视图
def news_search(request):
    """新闻搜索视图"""
    return news_list(request)  # 复用新闻列表视图的搜索功能

# 首页视图
def home(request):
    """首页视图，包含搜索框和可视化数据"""
    from datetime import timedelta
    from django.utils import timezone
    
    # 获取情感趋势数据（最近7天）
    sentiment_trend = sentiment_service.get_sentiment_trend(days=7)
    
    # 获取新闻统计数据
    news_stats = visualization_service.get_news_statistics()
    
    # 获取最近7天热度最高的10条新闻
    from news_analysis.repositories.news_repository import NewsRepository
    hot_news = NewsRepository.get_hot_news(days=7, limit=10)
    
    return render(request, 'home.html', {
        'sentiment_trend': sentiment_trend,
        'news_stats': news_stats,
        'hot_news': hot_news
    })

# 收藏新闻视图
@login_required
def collect_news(request, pk):
    """收藏/取消收藏新闻"""
    # 使用服务层切换收藏状态
    is_collected = news_service.toggle_collection(pk, request.user)
    
    if is_collected:
        messages.success(request, '成功收藏该新闻！')
    else:
        messages.success(request, '已取消收藏该新闻。')
    
    return redirect('news_detail', pk=pk)

# 添加评论视图
@login_required
def add_comment(request, pk):
    """添加评论"""
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            # 使用服务层添加评论
            news_service.add_comment(pk, request.user, content, parent_id)
            messages.success(request, '评论成功！')
        else:
            messages.error(request, '评论内容不能为空。')
    
    return redirect('news_detail', pk=pk)

# 点赞评论视图
@login_required
def like_comment(request, pk):
    """点赞/取消点赞评论"""
    # 使用服务层切换点赞状态
    news_service.toggle_like(pk, request.user)
    
    return redirect('news_detail', pk=request.POST.get('news_id'))

# 用户收藏列表视图
@login_required
def user_collections(request):
    """用户收藏的新闻列表"""
    # 使用服务层获取用户收藏列表
    collections = news_service.get_user_collections(request.user)
    
    # 分页处理
    paginator = Paginator(collections, 10)
    page = request.GET.get('page', 1)
    
    try:
        collections_page = paginator.page(page)
    except PageNotAnInteger:
        collections_page = paginator.page(1)
    except EmptyPage:
        collections_page = paginator.page(paginator.num_pages)
    
    return render(request, 'news/collections.html', {'collections': collections_page})
