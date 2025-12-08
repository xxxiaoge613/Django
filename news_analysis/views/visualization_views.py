from django.shortcuts import render
from django.http import JsonResponse
from django.db import models
from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer
from news_analysis.models import News, SentimentAnalysis
from collections import Counter
import jieba
from django.utils.timezone import now
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# 仪表盘视图
def dashboard(request):
    """可视化仪表盘视图"""
    try:
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
    analyzer = SentimentAnalyzer()
    trend_data = analyzer.get_sentiment_trend(days=days)
    
    return render(request, 'visualization/sentiment_trend.html', {
        'trend_data': trend_data,
        'days': days
    })

# 平台分布视图
def platform_distribution(request):
    """平台分布视图"""
    platform_data = get_platform_statistics()
    
    return render(request, 'visualization/platform_distribution.html', {
        'platform_data': platform_data
    })

# 关键词云视图
def keyword_cloud(request):
    """关键词云视图"""
    limit = int(request.GET.get('limit', 50))
    keywords = get_hot_keywords(limit=limit)
    
    return render(request, 'visualization/keyword_cloud.html', {
        'keywords': keywords,
        'limit': limit
    })

# 获取平台分布数据（用于趋势图）
def get_platform_distribution():
    """获取各平台新闻数量趋势分布"""
    try:
        # 1. 生成最近7天的完整日期列表
        end_date = now().date()
        dates = []
        for i in range(7):
            current_date = end_date - timedelta(days=6 - i)  # 从6天前到今天
            dates.append(current_date.strftime('%Y-%m-%d'))
        
        # 2. 获取所有有效新闻，不限制日期范围
        news_list = News.objects.filter(
            is_valid=True, 
            is_ad=False
        ).order_by('publish_time')
        
        # 3. 按日期和平台分组统计
        platform_trend = {}
        
        for news in news_list:
            # 格式化日期为YYYY-MM-DD
            date_key = news.publish_time.strftime('%Y-%m-%d')
            platform = news.platform
            
            if date_key not in platform_trend:
                platform_trend[date_key] = {}
            
            if platform not in platform_trend[date_key]:
                platform_trend[date_key][platform] = 0
            
            platform_trend[date_key][platform] += 1
        
        # 4. 获取所有平台
        platforms = set()
        for news in news_list:
            platforms.add(news.platform)
        platforms = sorted(platforms)
        
        # 5. 构建系列数据
        series = []
        # 预定义不同平台的颜色
        platform_colors = {
            '量子位': '#1890ff',
            '36kr': '#faad14'
        }
        
        for platform in platforms:
            # 为每个平台创建一个系列
            data = []
            for date in dates:
                # 获取该平台在该日期的新闻数量，默认为0
                count = platform_trend.get(date, {}).get(platform, 0)
                data.append(count)
            
            series.append({
                'name': platform,
                'type': 'line',
                'data': data,
                'itemStyle': {
                    'color': platform_colors.get(platform, '#999999')
                }
            })
        
        return {
            'dates': dates,
            'series': series,
            'platforms': platforms
        }
    except Exception as e:
        logger.error(f"获取平台分布数据失败: {e}")
        return {
            'dates': [],
            'series': [],
            'platforms': []
        }

# 获取平台统计数据（用于平台分布页面）
def get_platform_statistics():
    """获取各平台新闻数量统计"""
    try:
        # 统计各平台新闻数量
        platform_counts = News.objects.filter(is_valid=True, is_ad=False).values('platform').annotate(count=models.Count('id'))
        
        # 计算总新闻数
        total_news = sum(item['count'] for item in platform_counts)
        
        # 构建返回数据，包含平台名称、新闻数量和占比
        platform_data = []
        for item in platform_counts:
            percentage = (item['count'] / total_news) * 100 if total_news > 0 else 0
            platform_data.append({
                'platform': item['platform'],
                'count': item['count'],
                'percentage': percentage
            })
        
        return platform_data
    except Exception as e:
        logger.error(f"获取平台统计数据失败: {e}")
        return []

# 获取热门关键词
def get_hot_keywords(limit=50):
    """获取热门关键词"""
    try:
        from news_analysis.models import Keyword, News
        from django.db.models import Count
        
        # 从Keyword模型中获取所有有效新闻的关键词，按出现次数排序
        # 不限制时间范围，确保能获取到关键词
        hot_keywords = Keyword.objects.filter(
            news__is_valid=True,
            news__is_ad=False
        ).values('keyword').annotate(
            count=Count('keyword')
        ).order_by('-count')[:limit]
        
        # 如果从Keyword模型中没有获取到足够的关键词，回退到传统方法
        if not hot_keywords or len(hot_keywords) < limit:
            logger.info("从Keyword模型获取关键词不足，回退到传统方法")
            
            # 不限制时间范围，获取所有有效新闻
            news_list = News.objects.filter(
                is_valid=True, 
                is_ad=False
            )
            
            if not news_list:
                return []
            
            # 合并所有新闻标题和内容
            all_text = ' '.join([news.title + ' ' + news.content for news in news_list])
            
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
            
            # 获取前N个热门关键词
            hot_keywords = word_counts.most_common(limit)
            
            return [{
                'keyword': word,
                'count': count
            } for word, count in hot_keywords]
        
        # 格式化结果
        return [{
            'keyword': item['keyword'],
            'count': item['count']
        } for item in hot_keywords]
    except Exception as e:
        logger.error(f"获取热门关键词失败: {e}")
        return []

# 获取新闻统计数据
def get_news_statistics():
    """获取新闻统计数据"""
    try:
        # 总新闻数
        total_news = News.objects.filter(is_valid=True).count()
        
        # 有效新闻数（非广告）
        valid_news = News.objects.filter(is_valid=True, is_ad=False).count()
        
        # 广告新闻数
        ad_news = News.objects.filter(is_valid=True, is_ad=True).count()
        
        # 已分析情感的新闻数
        analyzed_news = SentimentAnalysis.objects.count()
        
        # 今日新增新闻数
        today = now().date()
        today_news = News.objects.filter(is_valid=True, publish_time__date=today).count()
        
        return {
            'total_news': total_news,
            'valid_news': valid_news,
            'ad_news': ad_news,
            'analyzed_news': analyzed_news,
            'today_news': today_news
        }
    except Exception as e:
        logger.error(f"获取新闻统计数据失败: {e}")
        return {
            'total_news': 0,
            'valid_news': 0,
            'ad_news': 0,
            'analyzed_news': 0,
            'today_news': 0
        }


# 仪表盘数据JSON接口
def dashboard_data(request):
    """提供仪表盘JSON数据，用于前端实时更新"""
    try:
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
