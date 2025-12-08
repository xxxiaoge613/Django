import pandas as pd
import re
import logging
from news_analysis.models import News

logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器，用于清洗和预处理新闻数据"""
    
    def __init__(self):
        # 广告关键词列表
        self.ad_keywords = [
            '广告', '推广', '赞助', '招商', '加盟', '代理',
            '热销', '包邮', '限时', '优惠', '促销', '抢购',
            '正品', '特价', '清仓', '甩卖', '折扣', '返利'
        ]
        
        # 广告模式正则表达式
        self.ad_patterns = [
            re.compile(r'【.*?广告.*?】'),
            re.compile(r'\[.*?推广.*?\]'),
            re.compile(r'广告.*?热线|咨询电话'),
            re.compile(r'QQ群|微信群|微信号|公众号'),
            re.compile(r'点击链接|访问官网|下载APP')
        ]
    
    def clean_news_data(self, news_data):
        """清洗单条新闻数据"""
        try:
            # 1. 缺失值处理
            if not news_data.get('title'):
                news_data['title'] = '无标题'
            
            if not news_data.get('content'):
                news_data['content'] = ''
            
            # 2. 识别广告新闻
            is_ad = self._is_ad_news(news_data)
            news_data['is_ad'] = is_ad
            
            # 3. 数据标准化
            news_data = self._standardize_data(news_data)
            
            # 4. 清洗新闻内容
            news_data['content'] = self._clean_content(news_data['content'])
            
            # 5. 计算数据质量分数
            quality_score = self._calculate_quality_score(news_data)
            
            return news_data, quality_score
        except Exception as e:
            logger.error(f"清洗单条新闻数据失败: {e}")
            return news_data, 0
    
    def clean_batch_news(self, news_list):
        """批量清洗新闻数据"""
        cleaned_news = []
        quality_scores = []
        
        for news in news_list:
            cleaned, score = self.clean_news_data(news)
            cleaned_news.append(cleaned)
            quality_scores.append(score)
        
        return cleaned_news, quality_scores
    
    def clean_from_database(self):
        """从数据库中读取新闻进行清洗"""
        logger.info("开始从数据库中清洗新闻数据")
        
        try:
            # 读取所有未清洗的新闻
            news_list = News.objects.filter(is_valid=True, is_ad=False)
            logger.info(f"找到 {news_list.count()} 条需要清洗的新闻")
            
            cleaned_count = 0
            ad_count = 0
            
            for news in news_list:
                # 将新闻对象转换为字典
                news_data = {
                    'id': news.id,
                    'title': news.title,
                    'content': news.content,
                    'publish_time': news.publish_time,
                    'url': news.url,
                    'platform': news.platform,
                    'source_id': news.source_id,
                    'author': news.author,
                    'read_count': news.read_count,
                    'is_valid': news.is_valid,
                    'is_ad': news.is_ad
                }
                
                # 清洗新闻数据
                cleaned_data, quality_score = self.clean_news_data(news_data)
                
                # 更新数据库
                news.title = cleaned_data['title']
                news.content = cleaned_data['content']
                news.is_ad = cleaned_data['is_ad']
                news.save()
                
                cleaned_count += 1
                if cleaned_data['is_ad']:
                    ad_count += 1
            
            logger.info(f"数据清洗完成，共清洗 {cleaned_count} 条新闻，识别 {ad_count} 条广告")
            return cleaned_count, ad_count
        except Exception as e:
            logger.error(f"从数据库中清洗新闻数据失败: {e}")
            return 0, 0
    
    def _is_ad_news(self, news_data):
        """识别广告新闻"""
        # 检查标题中是否包含广告关键词
        title = news_data.get('title', '')
        for keyword in self.ad_keywords:
            if keyword in title:
                return True
        
        # 检查内容中是否包含广告关键词
        content = news_data.get('content', '')
        ad_keyword_count = 0
        for keyword in self.ad_keywords:
            if keyword in content:
                ad_keyword_count += 1
        
        # 如果内容中广告关键词超过3个，认为是广告
        if ad_keyword_count >= 3:
            return True
        
        # 检查是否匹配广告正则模式
        for pattern in self.ad_patterns:
            if pattern.search(title) or pattern.search(content):
                return True
        
        # 检查内容长度，如果过短且包含广告特征，认为是广告
        if len(content) < 200:
            for keyword in ['广告', '推广', '赞助']:
                if keyword in content:
                    return True
        
        return False
    
    def _clean_content(self, content):
        """清洗新闻内容"""
        # 1. 移除HTML标签
        content = re.sub(r'<.*?>', '', content)
        
        # 2. 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 3. 移除特殊字符
        content = re.sub(r'[\r\n\t]', '', content)
        
        # 4. 移除广告标识
        for pattern in self.ad_patterns:
            content = pattern.sub('', content)
        
        # 5. 移除首尾空格
        content = content.strip()
        
        return content
    
    def _standardize_data(self, news_data):
        """标准化数据格式"""
        # 标准化作者名称
        if news_data.get('author') == '':
            news_data['author'] = '未知'
        
        # 标准化阅读量
        if not isinstance(news_data.get('read_count'), int):
            try:
                news_data['read_count'] = int(news_data['read_count'])
            except:
                news_data['read_count'] = 0
        
        # 确保阅读量为非负数
        news_data['read_count'] = max(0, news_data['read_count'])
        
        return news_data
    
    def _calculate_quality_score(self, news_data):
        """计算数据质量分数（0-100）"""
        score = 100
        
        # 1. 标题质量（20分）
        title = news_data.get('title', '')
        if len(title) < 5:
            score -= 10
        if len(title) > 100:
            score -= 5
        
        # 2. 内容质量（50分）
        content = news_data.get('content', '')
        content_length = len(content)
        
        if content_length < 100:
            score -= 20
        elif content_length < 500:
            score -= 10
        elif content_length > 5000:
            score -= 5
        
        # 3. 广告识别（20分）
        if news_data.get('is_ad'):
            score -= 20
        
        # 4. 完整性（10分）
        if not news_data.get('author'):
            score -= 5
        if not news_data.get('publish_time'):
            score -= 5
        
        return max(0, min(100, score))
    
    def get_data_quality_report(self):
        """生成数据质量报告"""
        from news_analysis.models import News
        
        try:
            total_news = News.objects.count()
            valid_news = News.objects.filter(is_valid=True).count()
            ad_news = News.objects.filter(is_ad=True).count()
            
            # 计算质量指标
            valid_rate = (valid_news / total_news) * 100 if total_news > 0 else 0
            ad_rate = (ad_news / total_news) * 100 if total_news > 0 else 0
            
            report = {
                'total_news': total_news,
                'valid_news': valid_news,
                'ad_news': ad_news,
                'valid_rate': round(valid_rate, 2),
                'ad_rate': round(ad_rate, 2)
            }
            
            logger.info(f"生成数据质量报告: {report}")
            return report
        except Exception as e:
            logger.error(f"生成数据质量报告失败: {e}")
            return {}
