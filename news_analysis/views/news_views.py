from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from news_analysis.models import News, Comment, Collection, Like
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# 新闻列表视图
def news_list(request):
    """新闻列表视图"""
    # 获取筛选条件
    platform = request.GET.get('platform', '')
    sentiment = request.GET.get('sentiment', '')
    search_query = request.GET.get('q', '')
    search_mode = request.GET.get('search_mode', 'keyword')  # 'keyword'或'title'
    
    # 构建查询
    query = Q(is_valid=True, is_ad=False)
    
    if platform:
        query &= Q(platform=platform)
    
    if sentiment:
        query &= Q(sentiment__sentiment_type=sentiment)
    
    if search_query:
        if search_mode == 'title':
            # 标题搜索：仅匹配标题
            query &= Q(title__icontains=search_query)
        else:
            # 关键词搜索：匹配标题、内容和关键词
            query &= (Q(title__icontains=search_query) | 
                     Q(content__icontains=search_query) | 
                     Q(keywords__keyword=search_query))
    
    # 获取新闻列表，使用distinct()避免因关键词关联导致的重复结果
    news_list = News.objects.filter(query).distinct().order_by('-publish_time')
    
    # 分页处理
    paginator = Paginator(news_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    
    # 获取所有平台选项，去重并转换为集合
    platforms = list(set(News.objects.filter(is_valid=True).values_list('platform', flat=True)))
    
    return render(request, 'news/news_list.html', {
        'news': news,
        'platforms': platforms,
        'selected_platform': platform,
        'selected_sentiment': sentiment,
        'search_query': search_query,
        'search_mode': search_mode
    })

# 新闻详情视图
def news_detail(request, pk):
    """新闻详情视图"""
    news = get_object_or_404(News, pk=pk, is_valid=True)
    
    # 增加阅读量
    news.read_count += 1
    news.save()
    
    # 获取评论列表
    comments = news.comments.filter(is_deleted=False, parent__isnull=True).order_by('-created_at')
    
    # 计算评论总数
    total_comments = news.comments.filter(is_deleted=False).count()
    
    # 检查用户是否已收藏该新闻
    is_collected = False
    if request.user.is_authenticated:
        is_collected = Collection.objects.filter(user=request.user, news=news).exists()
    
    # 获取相关推荐新闻
    related_news = News.objects.filter(
        Q(platform=news.platform) & ~Q(id=pk),
        is_valid=True,
        is_ad=False
    ).order_by('-publish_time')[:5]
    
    # 获取当前新闻的关键词（从新闻标题和内容中提取）
    hot_keywords = []
    try:
        from collections import Counter
        import jieba
        
        # 合并新闻标题和内容
        all_text = news.title + ' ' + news.content
        
        # 使用jieba分词
        words = jieba.cut(all_text)
        
        # 财经领域停用词表
        stopwords = set([
            # 通用停用词
            '的', '了', '和', '是', '在', '有', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
            '我', '他', '她', '它', '们', '我们', '你们', '他们', '她们', '它们', '这', '那', '这些', '那些', '这里', '那里',
            '对于', '关于', '至于', '按照', '根据', '通过', '经过', '由于', '因为', '所以', '因此', '从而', '于是', '然后', '但是', '然而',
            '却', '不过', '只是', '如果', '假如', '假设', '倘若', '要是', '只要', '只有', '除非', '虽然', '尽管', '即使', '即便', '哪怕',
            '或者', '要么', '否则', '不仅', '不但', '而且', '并且', '同时', '另外', '此外', '还有', '以及', '与', '同', '跟', '和', '及',
            '之', '的', '了', '着', '过', '呢', '吗', '吧', '啊', '呀', '哦', '啦', '唉', '哎', '嗨', '喂', '嗯', '哼',
            
            # 财经领域停用词
            '新闻', '报道', '消息', '据悉', '表示', '认为', '指出', '强调', '说明', '提到', '称', '说', '发布', '宣布', '公告',
            '通知', '声明', '通报', '报告', '汇报', '总结', '分析', '研究', '调查', '探讨', '讨论', '审议',
            '会议', '论坛', '峰会', '大会', '展会', '展览', '展示', '活动', '仪式', '典礼', '庆典', '庆祝', '纪念',
            '节日', '假期', '休息', '放假', '上班', '工作', '学习', '生活', '娱乐', '休闲', '旅游', '出行', '交通',
            '饮食', '住宿', '购物', '消费', '支出', '花费', '费用', '价格', '成本',
        ])
        
        # 过滤停用词和无意义词
        filtered_words = [word for word in words if len(word) > 1 and word not in stopwords]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 按热度排序，取前10个关键词
        hot_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"提取当前新闻关键词失败: {e}")
        # 如果提取失败，返回空列表
        hot_keywords = []
    
    # 检查用户是否点赞了每条评论
    if request.user.is_authenticated:
        for comment in comments:
            comment.is_liked = comment.likes.filter(user=request.user).exists()
            # 检查每条回复是否被用户点赞
            for reply in comment.replies.all():
                if not reply.is_deleted:
                    reply.is_liked = reply.likes.filter(user=request.user).exists()
    
    return render(request, 'news/news_detail.html', {
        'news': news,
        'comments': comments,
        'is_collected': is_collected,
        'total_comments': total_comments,
        'related_news': related_news,
        'hot_keywords': hot_keywords
    })

# 新闻搜索视图
def news_search(request):
    """新闻搜索视图"""
    return news_list(request)  # 复用新闻列表视图的搜索功能

# 首页视图
def home(request):
    """首页视图，包含搜索框和可视化数据"""
    from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer
    from news_analysis.views.visualization_views import get_platform_distribution, get_hot_keywords, get_news_statistics
    
    # 获取情感分析器实例
    analyzer = SentimentAnalyzer()
    
    # 获取情感趋势数据（最近7天）
    sentiment_trend = analyzer.get_sentiment_trend(days=7)
    
    # 获取情感分布数据
    sentiment_dist = analyzer.get_sentiment_distribution()
    
    # 获取平台分布数据
    platform_dist = get_platform_distribution()
    
    # 获取热门关键词数据
    hot_keywords = get_hot_keywords(limit=20)
    
    # 获取新闻统计数据
    news_stats = get_news_statistics()
    
    return render(request, 'home.html', {
        'sentiment_trend': sentiment_trend,
        'sentiment_dist': sentiment_dist,
        'platform_dist': platform_dist,
        'hot_keywords': hot_keywords,
        'news_stats': news_stats
    })

# 收藏新闻视图
@login_required
def collect_news(request, pk):
    """收藏/取消收藏新闻"""
    news = get_object_or_404(News, pk=pk, is_valid=True)
    
    # 检查是否已收藏
    collection, created = Collection.objects.get_or_create(user=request.user, news=news)
    
    if created:
        messages.success(request, '成功收藏该新闻！')
    else:
        collection.delete()
        messages.success(request, '已取消收藏该新闻。')
    
    return redirect('news_detail', pk=pk)

# 添加评论视图
@login_required
def add_comment(request, pk):
    """添加评论"""
    if request.method == 'POST':
        news = get_object_or_404(News, pk=pk, is_valid=True)
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            comment_data = {
                'news': news,
                'user': request.user,
                'content': content
            }
            
            if parent_id:
                parent_comment = get_object_or_404(Comment, pk=parent_id)
                comment_data['parent'] = parent_comment
            
            Comment.objects.create(**comment_data)
            messages.success(request, '评论成功！')
        else:
            messages.error(request, '评论内容不能为空。')
    
    return redirect('news_detail', pk=pk)

# 点赞评论视图
@login_required
def like_comment(request, pk):
    """点赞/取消点赞评论"""
    comment = get_object_or_404(Comment, pk=pk)
    
    # 检查是否已点赞
    like, created = Like.objects.get_or_create(user=request.user, comment=comment)
    
    if not created:
        like.delete()
    
    return redirect('news_detail', pk=comment.news.id)

# 用户收藏列表视图
@login_required
def user_collections(request):
    """用户收藏的新闻列表"""
    collections = Collection.objects.filter(user=request.user).order_by('-created_at')
    
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
