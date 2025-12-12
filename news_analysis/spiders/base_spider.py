import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from django.utils.timezone import make_aware, now, timezone
import logging
import time
import random
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseSpider(ABC):
    """爬虫基类，定义通用的爬虫接口和方法"""
    
    def __init__(self, platform_name):
        self.platform_name = platform_name
        self.session = requests.Session()
        # 设置请求头，模拟浏览器
        self._set_headers()
        # 记录请求次数
        self.request_count = 0
    
    def _set_headers(self):
        """设置请求头"""
        # 随机选择User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/118.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/17.2',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://www.baidu.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(headers)
    
    def _make_request(self, url, method='GET', **kwargs):
        """封装请求方法，添加反爬措施"""
        # 随机延迟，避免请求过于频繁 - 增加延迟时间，减少对网站的访问压力
        delay = random.uniform(2, 5)
        logger.info(f"请求URL: {url}, 延迟: {delay}秒")
        time.sleep(delay)
        
        # 增加请求计数
        self.request_count += 1
        
        # 每10个请求更换一次User-Agent
        if self.request_count % 10 == 0:
            self._set_headers()
            logger.info("更换User-Agent")
        
        # 发送请求
        try:
            response = self.session.request(method, url, timeout=15, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None
    
    @abstractmethod
    def crawl_news_list(self, page=1):
        """爬取新闻列表页"""
        pass
    
    @abstractmethod
    def crawl_news_detail(self, news_url, basic_info):
        """爬取新闻详情页"""
        pass
    
    def parse_datetime(self, date_str):
        """解析日期字符串为datetime对象，支持相对时间格式"""
        if not date_str:
            return now()
        
        try:
            from datetime import datetime as dt, timezone as datetime_timezone
            from django.utils.timezone import make_aware, get_current_timezone
            
            # 清理字符串，移除不必要的字符
            date_str = date_str.strip().replace('\n', '').replace('\r', '')
            
            # 特殊处理36氪RSS feed的日期格式
            # 格式1: 2025-12-08 13:57:12  +0800（带+0800时区偏移）
            # 格式2: Wed, 08 Dec 2025 08:31:00 GMT（RSS标准格式，GMT/UTC时间）
            
            # 首先尝试处理RSS标准格式，这是36kr实际返回的格式
            if re.match(r'^\w+, \d{1,2} \w+ \d{4} \d{2}:\d{2}:\d{2} GMT$', date_str):
                # 解析RSS标准格式：Wed, 08 Dec 2025 08:31:00 GMT
                dt_obj = dt.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')
                # 这个时间是GMT/UTC时间，需要转换为北京时间（UTC+8）
                # 设置为UTC时间
                utc_dt = dt_obj.replace(tzinfo=datetime_timezone.utc)
                # 转换为北京时间（UTC+8）
                beijing_dt = utc_dt.astimezone(get_current_timezone())
                return beijing_dt
            
            # 处理格式1: 2025-12-08 13:57:12  +0800
            elif re.search(r'\s+\+0800', date_str):
                # 使用正则表达式提取不带时区的日期时间部分
                dt_str = re.sub(r'\s+\+0800', '', date_str).strip()
                # 解析日期时间
                publish_time = dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                # 使用Django的make_aware函数将datetime对象转换为带有时区的对象
                return make_aware(publish_time)
            
            # 获取当前时间，使用不带时区的datetime.now()
            current_time = datetime.now()
            
            # 处理不同的时间格式
            if "分钟前" in date_str:
                minutes = re.search(r'(\d+)', date_str)
                if minutes:
                    minutes = int(minutes.group(1))
                    publish_time = current_time - timedelta(minutes=minutes)
                    return make_aware(publish_time)
            elif "小时前" in date_str:
                hours = re.search(r'(\d+)', date_str)
                if hours:
                    hours = int(hours.group(1))
                    publish_time = current_time - timedelta(hours=hours)
                    return make_aware(publish_time)
            elif "天前" in date_str:
                days = re.search(r'(\d+)', date_str)
                if days:
                    days = int(days.group(1))
                    publish_time = current_time - timedelta(days=days)
                    return make_aware(publish_time)
            elif "昨天" in date_str:
                publish_time = current_time - timedelta(days=1)
                # 尝试提取具体时间
                time_part = re.search(r'(\d+:\d+(?::\d+)?)', date_str)
                if time_part:
                    time_str_part = time_part.group(1)
                    # 根据时间部分是否包含秒数选择格式
                    if ":" in time_str_part and len(time_str_part.split(":")) > 2:
                        # 包含秒数
                        dt_str = f"{publish_time.year}-{publish_time.month:02d}-{publish_time.day:02d} {time_str_part}"
                        publish_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        # 不包含秒数
                        dt_str = f"{publish_time.year}-{publish_time.month:02d}-{publish_time.day:02d} {time_str_part}"
                        publish_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
                return make_aware(publish_time)
            elif "前天" in date_str:
                publish_time = current_time - timedelta(days=2)
                # 尝试提取具体时间
                time_part = re.search(r'(\d+:\d+(?::\d+)?)', date_str)
                if time_part:
                    time_str_part = time_part.group(1)
                    # 根据时间部分是否包含秒数选择格式
                    if ":" in time_str_part and len(time_str_part.split(":")) > 2:
                        # 包含秒数
                        dt_str = f"{publish_time.year}-{publish_time.month:02d}-{publish_time.day:02d} {time_str_part}"
                        publish_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        # 不包含秒数
                        dt_str = f"{publish_time.year}-{publish_time.month:02d}-{publish_time.day:02d} {time_str_part}"
                        publish_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
                return make_aware(publish_time)
            elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str):
                # 处理"2025-12-05 18:55:00"格式（带秒数，优先处理）
                publish_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                return make_aware(publish_time)
            elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', date_str):
                # 处理"2025-12-05 18:55"格式（不带秒数）
                publish_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                return make_aware(publish_time)
            elif re.match(r'\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str):
                # 处理"12-05 18:55:00"格式（带秒数）
                dt_str = f"2025-{date_str}"
                publish_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                return make_aware(publish_time)
            elif re.match(r'\d{2}-\d{2} \d{2}:\d{2}', date_str):
                # 处理"12-05 18:55"格式（不带秒数）
                dt_str = f"2025-{date_str}"
                publish_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
                return make_aware(publish_time)
            elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                # 处理"2025-12-05"格式
                publish_time = datetime.strptime(date_str, '%Y-%m-%d')
                return make_aware(publish_time)
            elif re.match(r'\d{2}-\d{2}', date_str):
                # 处理"12-05"格式
                dt_str = f"2025-{date_str}"
                publish_time = datetime.strptime(dt_str, '%Y-%m-%d')
                return make_aware(publish_time)
            elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s+\+\d{4}', date_str):
                # 专门处理36氪RSS feed的日期格式：2025-12-08 13:57:12  +0800
                try:
                    # 移除多余的空格，保留时区前的一个空格
                    date_str_clean = re.sub(r'\s+\+', ' +', date_str)
                    # 直接解析带有时区的日期时间
                    publish_time = datetime.strptime(date_str_clean, '%Y-%m-%d %H:%M:%S %z')
                    # 返回带有时区的datetime对象，Django会自动处理时区转换
                    return publish_time
                except ValueError:
                    pass
            else:
                # 尝试多种绝对日期格式
                date_formats = [
                    '%Y/%m/%d %H:%M:%S',
                    '%Y/%m/%d',
                    '%m/%d/%Y %H:%M:%S',
                    '%m/%d/%Y',
                    '%H:%M',
                    '%Y-%m-%d %H:%M:%S %z',  # 处理带时区偏移的日期格式，如 2025-12-08 13:57:12 +0800
                    '%a, %d %b %Y %H:%M:%S %z',  # 处理 RSS 标准日期格式，如 Wed, 08 Dec 2025 13:57:12 +0800
                    '%a, %d %b %Y %H:%M:%S %Z'  # 处理 RFC 822 格式，如 Mon, 08 Dec 2025 07:20:03 GMT
                ]
                
                for fmt in date_formats:
                    try:
                        dt_obj = datetime.strptime(date_str, fmt)
                        # 如果年份不完整，添加当前年份
                        if dt_obj.year == 1900:
                            dt_obj = dt_obj.replace(year=current_time.year)
                        
                        # 检查是否为带时区的日期
                        if hasattr(dt_obj, 'tzinfo') and dt_obj.tzinfo is not None and dt_obj.tzinfo.utcoffset(dt_obj) is not None:
                            # 已带时区，直接返回
                            return dt_obj
                        else:
                            # 不带时区，使用Django的make_aware函数将其转换为带有时区的对象
                            # make_aware会自动使用settings.TIME_ZONE中设置的时区（上海时区，UTC+8）
                            return make_aware(dt_obj)
                    except ValueError:
                        continue
                
                logger.warning(f"无法解析日期格式: {date_str}")
                return make_aware(datetime.now())
        except Exception as e:
            logger.error(f"解析日期失败: {e}")
            return make_aware(datetime.now())
    
    def save_to_database(self, news_data):
        """将爬取的数据保存到数据库"""
        import threading
        from django.db import connection
        
        def _sync_save():
            """同步保存数据的内部函数"""
            from news_analysis.models import News
            import django.db.models as models
            
            try:
                # 检查是否已存在相同的新闻（通过url或source_id去重）
                existing_news = News.objects.filter(
                    models.Q(url=news_data['url']) | models.Q(source_id=news_data['source_id'])
                ).first()
                
                if existing_news:
                    # 新闻已存在，更新正文内容和其他信息
                    logger.info(f"新闻已存在，更新内容: {news_data['title']}")
                    
                    # 更新新闻字段
                    update_fields = ['content', 'read_count', 'author', 'publish_time']
                    
                    # 只更新有变化的字段
                    for field in update_fields:
                        if field in news_data and getattr(existing_news, field) != news_data[field]:
                            setattr(existing_news, field, news_data[field])
                    
                    existing_news.save()
                    
                    # 重新提取关键词和分析情感
                    self.auto_extract_keywords(existing_news)
                    self.auto_analyze_sentiment(existing_news)
                    
                    return existing_news, False
                
                # 创建新闻对象
                news = News.objects.create(**news_data)
                logger.info(f"成功保存新闻: {news_data['title']}")
                
                # 自动提取关键词
                self.auto_extract_keywords(news)
                
                # 自动进行情感分析
                self.auto_analyze_sentiment(news)
                
                return news, True
            except Exception as e:
                logger.error(f"保存新闻到数据库失败: {e}")
                return None, False
            finally:
                # 确保数据库连接关闭
                connection.close()
        
        # 在新线程中执行数据库操作
        thread = threading.Thread(target=_sync_save)
        thread.start()
        thread.join()
        
        # 获取结果 - 由于线程执行，这里无法直接返回结果
        # 但我们可以通过日志了解保存情况
        return None, True
    
    def auto_analyze_sentiment(self, news):
        """自动分析新闻情感"""
        from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer
        from news_analysis.models import SentimentAnalysis
        
        try:
            logger.info(f"开始自动分析新闻情感: {news.title[:30]}...")
            
            # 创建情感分析器实例
            analyzer = SentimentAnalyzer()
            
            # 分析新闻情感
            sentiment_result = analyzer.analyze_news_sentiment(news)
            
            # 保存分析结果到数据库 - 使用get_or_create避免唯一约束冲突
            sentiment, created = SentimentAnalysis.objects.get_or_create(
                news=news,
                defaults={
                    'sentiment_score': sentiment_result['sentiment_score'],
                    'sentiment_type': sentiment_result['sentiment_type']
                }
            )
            
            # 如果已存在记录，更新情感分析结果
            if not created:
                sentiment.sentiment_score = sentiment_result['sentiment_score']
                sentiment.sentiment_type = sentiment_result['sentiment_type']
                sentiment.save()
            
            logger.info(f"新闻情感分析完成: {news.title[:30]}..., 情感类型: {sentiment_result['sentiment_type']}")
        except Exception as e:
            logger.error(f"自动分析新闻情感失败: {e}")
    
    def auto_extract_keywords(self, news):
        """自动提取新闻关键词并保存到数据库"""
        from news_analysis.models import Keyword
        from news_analysis.utils.keyword_extractor import extract_news_keywords
        
        try:
            logger.info(f"开始自动提取新闻关键词: {news.title[:30]}...")
            
            # 使用关键词提取工具提取关键词
            keywords = extract_news_keywords(news, limit=10)
            
            if not keywords:
                logger.info(f"未提取到有效关键词: {news.title[:30]}...")
                return
            
            # 保存关键词到数据库
            for keyword_info in keywords:
                # 创建或更新关键词
                Keyword.objects.get_or_create(
                    news=news,
                    keyword=keyword_info['keyword'],
                    defaults={'weight': keyword_info['weight']}
                )
            
            logger.info(f"关键词提取完成: {news.title[:30]}..., 共提取 {len(keywords)} 个关键词")
        except Exception as e:
            logger.error(f"自动提取关键词失败: {e}")
    
    def close(self):
        """关闭爬虫资源"""
        self.session.close()
