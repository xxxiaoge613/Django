import pandas as pd
import re
import logging
from news_analysis.models import News

logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器，用于清洗和预处理新闻数据"""
    
    def __init__(self):
        pass
    
    def clean_news_data(self, news_data):
        """清洗单条新闻数据"""
        try:
            # 1. 缺失值处理
            if not news_data.get('title'):
                news_data['title'] = '无标题'
            
            if not news_data.get('content'):
                news_data['content'] = ''
            
            # 2. 数据标准化
            news_data = self._standardize_data(news_data)
            
            # 3. 清洗新闻内容
            news_data['content'] = self._clean_content(news_data['content'])
            
            # 4. 计算数据质量分数
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
            news_list = News.objects.filter(is_valid=True)
            logger.info(f"找到 {news_list.count()} 条需要清洗的新闻")
            
            cleaned_count = 0
            
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
                    'is_valid': news.is_valid
                }
                
                # 清洗新闻数据
                cleaned_data, quality_score = self.clean_news_data(news_data)
                
                # 更新数据库
                news.title = cleaned_data['title']
                news.content = cleaned_data['content']
                news.save()
                
                cleaned_count += 1
            
            logger.info(f"数据清洗完成，共清洗 {cleaned_count} 条新闻")
            return cleaned_count, 0
        except Exception as e:
            logger.error(f"从数据库中清洗新闻数据失败: {e}")
            return 0, 0
    
    def _clean_content(self, content):
        """清洗新闻内容"""
        # 1. 移除HTML标签
        content = re.sub(r'<.*?>', '', content)
        
        # 2. 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 3. 移除特殊字符
        content = re.sub(r'[\r\n\t]', '', content)
        
        # 4. 移除首尾空格
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
        
        # 3. 完整性（10分）
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
            
            # 计算质量指标
            valid_rate = (valid_news / total_news) * 100 if total_news > 0 else 0
            
            report = {
                'total_news': total_news,
                'valid_news': valid_news,
                'valid_rate': round(valid_rate, 2)
            }
            
            logger.info(f"生成数据质量报告: {report}")
            return report
        except Exception as e:
            logger.error(f"生成数据质量报告失败: {e}")
            return {}
