import logging
from collections import Counter
import jieba
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count
from news_analysis.models import News, SentimentAnalysis, Keyword
from news_analysis.services.keyword_service import KeywordService

logger = logging.getLogger(__name__)

class VisualizationService:
    """可视化服务层，封装可视化数据获取的业务逻辑"""
    
    def __init__(self):
        self.keyword_service = KeywordService()
    
    def get_platform_distribution(self):
        """获取各平台新闻数量趋势分布"""
        try:
            # 1. 生成最近7天的完整日期列表
            end_date = now().date()
            dates = []
            for i in range(7):
                current_date = end_date - timedelta(days=6 - i)  # 从6天前到今天
                dates.append(current_date.strftime('%m-%d'))
            
            # 2. 获取所有有效新闻，不限制日期范围
            news_list = News.objects.filter(
                is_valid=True
            ).order_by('publish_time')
            
            # 3. 按日期和平台分组统计
            platform_trend = {}
            
            for news in news_list:
                # 格式化日期为MM-DD
                date_key = news.publish_time.strftime('%m-%d')
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
    
    def get_platform_statistics(self):
        """获取各平台新闻数量统计"""
        try:
            # 统计各平台新闻数量
            platform_counts = News.objects.filter(is_valid=True).values('platform').annotate(count=Count('id'))
            
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
    
    def get_hot_keywords(self, limit=50):
        """获取热门关键词"""
        try:
            # 财经领域停用词表
            stopwords = set([
                # 通用停用词
                '的', '了', '和', '是', '在', '有', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
                '我', '他', '她', '它', '们', '我们', '你们', '他们', '她们', '它们', '这', '那', '这些', '那些', '这里', '那里',
                '对于', '关于', '至于', '按照', '根据', '通过', '经过', '由于', '因为', '所以', '因此', '从而', '于是', '然后', '但是', '然而',
                '却', '不过', '只是', '如果', '假如', '假设', '倘若', '要是', '只要', '只有', '除非', '虽然', '尽管', '即使', '即便', '哪怕',
                '或者', '要么', '否则', '不仅', '不但', '而且', '并且', '同时', '另外', '此外', '还有', '以及', '与', '同', '跟', '和', '及',
                '之', '的', '了', '着', '过', '呢', '吗', '吧', '啊', '呀', '哦', '啦', '唉', '哎', '嗨', '喂', '嗯', '哼', '可以', '可是', '可能', '应该', '一定', '能', '不能', '会', '不会', '公司', '万亿元', '显示', '有限公司', '问题', '集团',
            ])
            
            # 从Keyword模型中获取所有有效新闻的关键词，按出现次数排序
            # 不限制时间范围，确保能获取到关键词
            hot_keywords = Keyword.objects.filter(
                news__is_valid=True
            ).values('keyword').annotate(
                count=Count('keyword')
            ).order_by('-count')[:limit*2]  # 获取更多关键词以便过滤后仍有足够数量
            
            # 如果从Keyword模型中没有获取到足够的关键词，回退到传统方法
            if not hot_keywords or len([item for item in hot_keywords if not item['keyword'].isdigit() and item['keyword'] not in stopwords]) < limit:
                logger.info("从Keyword模型获取关键词不足，回退到传统方法")
                
                # 不限制时间范围，获取所有有效新闻
                news_list = News.objects.filter(
                    is_valid=True
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
                '之', '的', '了', '着', '过', '呢', '吗', '吧', '啊', '呀', '哦', '啦', '唉', '哎', '嗨', '喂', '嗯', '哼', '可以', '可是', '可能', '应该', '一定', '能', '不能', '会', '不会',
                    
                    # 财经领域停用词
                    '新闻', '报道', '消息', '据悉', '获悉', '表示', '认为', '指出', '强调', '说明', '提到', '称', '说', '发布', '宣布', '公告',
                    '通知', '声明', '通报', '报告', '汇报', '总结', '分析', '研究', '调查', '探讨', '讨论', '审议',
                    '会议', '论坛', '峰会', '大会', '展会', '展览', '展示', '活动', '仪式', '典礼', '庆典', '庆祝', '纪念',
                    '节日', '假期', '休息', '放假', '上班', '工作', '学习', '生活', '娱乐', '休闲', '旅游', '出行', '交通',
                    '饮食', '住宿', '购物', '消费', '支出', '花费', '费用', '价格', '成本', '相关', '继续', '简称', '公司', '万亿元', '显示', '有限公司', '问题', '集团',
                ])
                
                # 过滤停用词、无意义词和纯数字
                filtered_words = [word for word in words if len(word) > 1 and word not in stopwords and not word.isdigit()]
                
                # 统计词频
                word_counts = Counter(filtered_words)
                
                # 获取前N个热门关键词
                hot_keywords = word_counts.most_common(limit)
                
                return [{
                    'keyword': word,
                    'count': count
                } for word, count in hot_keywords]
            
            # 格式化结果，过滤掉纯数字关键词和停用词
            return [{
                'keyword': item['keyword'],
                'count': item['count']
            } for item in hot_keywords if not item['keyword'].isdigit() and item['keyword'] not in stopwords]
        except Exception as e:
            logger.error(f"获取热门关键词失败: {e}")
            return []
    
    def get_news_statistics(self):
        """获取新闻统计数据"""
        try:
            # 总新闻数
            total_news = News.objects.filter(is_valid=True).count()
            
            # 有效新闻数
            valid_news = total_news
            
            # 已分析情感的新闻数
            analyzed_news = SentimentAnalysis.objects.count()
            
            # 今日新增新闻数
            today = now().date()
            today_news = News.objects.filter(is_valid=True, publish_time__date=today).count()
            
            return {
                'total_news': total_news,
                'valid_news': valid_news,
                'analyzed_news': analyzed_news,
                'today_news': today_news
            }
        except Exception as e:
            logger.error(f"获取新闻统计数据失败: {e}")
            return {
                'total_news': 0,
                'valid_news': 0,
                'analyzed_news': 0,
                'today_news': 0
            }