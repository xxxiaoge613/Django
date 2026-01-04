#!/usr/bin/env python3
"""
关键词提取工具模块
"""

import jieba
from collections import Counter
import logging

logger = logging.getLogger(__name__)

def extract_keywords(text, limit=10, stopwords=None):
    """从文本中提取关键词
    
    Args:
        text: 要提取关键词的文本
        limit: 提取的关键词数量上限
        stopwords: 自定义停用词表
    
    Returns:
        list: 提取的关键词列表，每个元素包含keyword和weight
    """
    try:
        import re
        
        # 过滤HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 过滤URL和图片链接
        text = re.sub(r'http[s]?://[^\s]+', '', text)
        
        # 过滤图片相关的属性和路径
        text = re.sub(r'img\.36krcdn\.com', '', text)
        text = re.sub(r'hsossms', '', text)
        text = re.sub(r'\w+\.jpg|\w+\.png|\w+\.gif|\w+\.bmp', '', text)
        
        # 默认停用词表
        default_stopwords = set([
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
            
            # 网站特定停用词
            '36氪', '原文', '阅读', '全文', '更多', '点击', '查看', '了解', '详情',
            
            # 无意义关键词
            '具身', '具身化', '2025', '2024', '2023', '2022', '2021', '2020', '获悉', '相关', '继续', '简称', '公司', '万亿元', '显示', '有限公司', '问题', '集团',
        ])
        
        # 合并停用词表
        if stopwords:
            final_stopwords = default_stopwords.union(set(stopwords))
        else:
            final_stopwords = default_stopwords
        
        # 使用jieba分词
        words = jieba.cut(text)
        
        # 过滤停用词和无意义词
        filtered_words = []
        
        for word in words:
            if len(word) > 1 and word not in final_stopwords:
                # 过滤日期格式
                import re
                
                # 匹配各种日期格式
                is_date = False
                
                # 匹配单个年份，如2025
                if re.match(r'^\d{4}$', word):
                    is_date = True
                # 匹配纯数字日期，如20251203、2306125109671464
                elif re.match(r'\d{4,}', word):
                    is_date = True
                # 匹配YYYY-MM-DD或YYYY/MM/DD格式
                elif re.match(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', word):
                    is_date = True
                # 匹配DD-MM-YYYY或MM-DD-YYYY格式
                elif re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', word):
                    is_date = True
                # 匹配包含时间的日期格式
                elif re.match(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}', word):
                    is_date = True
                
                if not is_date:
                    filtered_words.append(word)
        
        if not filtered_words:
            return []
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 获取前N个关键词
        top_words = word_counts.most_common(limit)
        
        # 计算权重（基于词频）
        total_count = sum(word_counts.values())
        keywords = []
        for word, count in top_words:
            weight = count / total_count
            keywords.append({
                'keyword': word,
                'weight': weight,
                'count': count
            })
        
        return keywords
    except Exception as e:
        logger.error(f"提取关键词失败: {e}")
        return []


def extract_news_keywords(news, limit=10):
    """从新闻对象中提取关键词
    
    Args:
        news: 新闻对象，包含title和content属性
        limit: 提取的关键词数量上限
    
    Returns:
        list: 提取的关键词列表，每个元素包含keyword和weight
    """
    try:
        # 合并标题和内容
        text = news.title + ' ' + news.content
        
        # 提取关键词
        return extract_keywords(text, limit=limit)
    except Exception as e:
        logger.error(f"从新闻提取关键词失败: {e}")
        return []