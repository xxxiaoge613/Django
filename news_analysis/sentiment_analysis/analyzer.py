from snownlp import SnowNLP
import logging
from collections import Counter
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """情感分析器，基于SnowNLP模型实现新闻情感分析"""
    
    def __init__(self):
        # 自定义财经领域情感词典
        self.positive_words = self._load_financial_positive_words()
        self.negative_words = self._load_financial_negative_words()
        
    def _load_financial_positive_words(self):
        """加载财经领域正面情感词"""
        return {
            '增长': 2.0, '上涨': 2.0, '创新高': 2.5, '盈利': 2.0,
            '利润': 1.5, '收益': 1.8, '投资': 1.0, '机会': 1.5, '发展': 1.5,
            '成功': 2.0, '突破': 2.0, '利好': 2.5, '优势': 1.5, '强劲': 1.8,
            '繁荣': 2.0, '景气': 1.8, '复苏': 2.0, '上升': 1.5, '活跃': 1.2,
            '稳健': 1.5, '良好': 1.8, '高': 1.0, '创新': 1.5, '龙头': 2.0,
            '领先': 1.8, '优质': 1.5, '高效': 1.5, '潜力': 1.8, '价值': 1.5,
            '回报': 2.0, '扩张': 1.5, '改善': 1.8, '提升': 1.8, '超预期': 2.5,
            '好转': 2.0, '获得': 1.5, '巩固': 1.8, '机遇': 2.0, '增强': 1.8,
            '加速': 2.0, '扩大': 1.8, '创新': 1.5, '提升': 1.8, '领先': 1.8,
            '优质': 1.5, '高效': 1.5, '潜力': 1.8, '价值': 1.5, '回报': 2.0
        }
    
    def _load_financial_negative_words(self):
        """加载财经领域负面情感词"""
        return {
            # 核心负面词汇
            '下跌': -2.0, '亏损': -2.0, '下降': -1.5, '崩盘': -3.0, '倒闭': -3.0,
            '风险': -2.0, '危机': -2.5, '泡沫': -2.0, '贬值': -2.0, '下滑': -1.8,
            '疲软': -1.5, '恶化': -2.0, '利空': -2.5, '劣势': -1.5, '低迷': -1.8,
            '衰退': -2.0, '萎缩': -1.8, '停滞': -1.5, '破产': -3.0, '债务': -1.8,
            '坏账': -2.0, '违约': -2.5, '损失': -2.0, '困境': -2.0, '压力': -1.5,
            '挑战': -1.2, '低': -1.0, '负面': -2.0, '问题': -1.5, '暴跌': -3.0,
            
            # 金融诈骗相关词汇
            '被骗': -3.0, '诈骗': -3.0, '欺诈': -3.0, '受骗': -3.0, '行骗': -3.0,
            '骗局': -3.0, '欺诈案': -3.0, '诈骗案': -3.0, '金融诈骗': -3.5,
            '财务欺诈': -3.5, '骗局': -3.0, '圈套': -3.0, '陷阱': -3.0,
            
            # 业绩下滑相关词汇
            '大幅下滑': -2.5, '严重下滑': -2.5, '持续下滑': -2.5, '急剧下滑': -2.5,
            '销量下滑': -2.0, '利润下滑': -2.5, '收入下滑': -2.5, '业绩下滑': -2.5,
            
            # 市场负面词汇
            '熊市': -2.5, '看空': -2.0, '抛售': -2.0, '大跌': -2.5, '暴跌': -3.0,
            '跳水': -3.0, '雪崩': -3.0, '崩盘': -3.0, '破位': -2.0, '跌停': -3.0,
            
            # 企业负面词汇
            '裁员': -2.0, '裁撤': -2.0, '解雇': -2.0, '失业': -2.0, '失业率上升': -2.5,
            '倒闭': -3.0, '破产': -3.0, '清算': -3.0, '解散': -3.0, '关停': -2.5,
            '违约': -2.5, '债务违约': -3.0, '信用违约': -3.0, '拖欠': -2.0,
            
            # 负面事件词汇
            '投诉': -1.8, '诉讼': -2.0, '调查': -2.0, '处罚': -2.5, '罚款': -2.5,
            '违规': -2.5, '违法': -3.0, '丑闻': -3.0, '曝光': -2.0, '危机': -2.5,
            '事故': -2.5, '灾难': -3.0, '损失惨重': -3.0, '失败': -2.5,
            
            # 产品相关负面词汇
            '质量问题': -2.5, '召回': -2.5, '产品召回': -3.0, '投诉': -1.8, '品牌声誉受损': -2.5,
            '故障': -2.0, '缺陷': -2.5, '安全隐患': -3.0, '不合格': -2.5, '劣质': -2.5,
            
            # 人员相关负面词汇
            '离职': -2.0, '核心人员离职': -3.0, '技术人员离职': -2.5, '高管离职': -2.5,
            '人才流失': -3.0, '裁员': -2.0, '解雇': -2.0, '失业': -2.0, '失业率上升': -2.5,
            
            # 成本相关负面词汇
            '成本上升': -2.0, '成本压力': -2.5, '成本骤增': -3.0, '价格上涨': -2.0,
            '原材料上涨': -2.5, '成本增加': -2.0, '费用增加': -1.8, '开支增大': -1.8,
            
            # 项目相关负面词汇
            '项目失败': -2.5, '研发受挫': -2.5, '项目停滞': -2.0, '研发延迟': -2.0,
            '进展缓慢': -1.8, '受挫': -2.0, '受阻': -2.0, '延迟': -1.8,
            
            # 其他负面词汇
            '放缓': -1.5, '增速放缓': -2.0, '停滞': -2.0, '收缩': -2.0, '紧缩': -2.0,
            '收紧': -2.0, '堪忧': -2.0, '受损': -2.0, '破坏': -2.0, '抢占': -1.5,
            '断裂': -2.5, '短缺': -2.0, '紧张': -1.5, '恶化': -2.0, '疲软': -1.5,
            '低迷': -1.8, '衰退': -2.0, '萎缩': -1.8, '亏损': -2.0, '赤字': -2.0,
            '坏账': -2.0, '呆账': -2.0, '滞销': -2.0, '积压': -2.0, '过剩': -1.5,
            '泡沫': -2.0, '高估': -1.5, '风险': -2.0, '威胁': -2.0, '挑战': -1.2,
            '发酵': -2.0, '持续发酵': -2.5, '大跌': -2.5, '骤增': -2.0
        }
    
    def _load_financial_neutral_words(self):
        """加载财经领域中性情感词"""
        return {
            '发布': 0.0, '举办': 0.0, '探讨': 0.0, '符合预期': 0.0, '稳定': 0.0,
            '调整': 0.0, '变动': 0.0, '更新': 0.0, '强调': 0.0, '显示': 0.0,
            '签订': 0.0, '协议': 0.0, '申请': 0.0, '活动': 0.0, '解答': 0.0,
            '报告': 0.0, '数据': 0.0, '会议': 0.0, '趋势': 0.0, '平淡': 0.0,
            '宣布': 0.0, '上任': 0.0, '规模': 0.0, '保持': 0.0, '发布': 0.0
        }
    
    def analyze_sentiment(self, text):
        """分析单篇文本的情感
        
        Args:
            text: 要分析的文本内容
            
        Returns:
            dict: 情感分析结果，包含情感得分、情感类型
        """
        try:
            # 确保文本是有效的字符串
            if not text or not isinstance(text, str):
                return {
                    'sentiment_score': 0.5,
                    'sentiment_type': '中性',
                    'snow_score': 0.5,
                    'financial_score': 0.5
                }
            
            # 使用SnowNLP进行基础情感分析，增加异常处理
            snow_score = 0.5  # 默认值
            try:
                s = SnowNLP(text)
                snow_score = s.sentiments
                # 确保snow_score是有效的数值
                if snow_score is None or not isinstance(snow_score, (int, float)):
                    snow_score = 0.5
            except Exception as e:
                logger.debug(f"SnowNLP分析失败，使用默认值: {e}")
                snow_score = 0.5
            
            # 结合自定义财经词典优化得分
            financial_score = self._calculate_financial_score(text)
            
            # 综合得分（SnowNLP得分占5%，自定义词典得分占95%）
            final_score = (snow_score * 0.05) + (financial_score * 0.95)
            
            # 确保得分在0-1之间
            final_score = max(0.0, min(1.0, final_score))
            
            # 确定情感类型 - 调整阈值，提高正面新闻识别率
            if final_score > 0.52:
                sentiment_type = '正面'
            elif final_score < 0.50:
                sentiment_type = '负面'
            else:
                sentiment_type = '中性'
            
            return {
                'sentiment_score': round(final_score, 4),
                'sentiment_type': sentiment_type,
                'snow_score': round(snow_score, 4),
                'financial_score': round(financial_score, 4)
            }
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {
                'sentiment_score': 0.5,
                'sentiment_type': '中性',
                'snow_score': 0.5,
                'financial_score': 0.5
            }
    
    def _calculate_financial_score(self, text):
        """基于自定义财经词典计算情感得分，考虑否定词、程度副词和负面组合词"""
        # 确保文本是有效的字符串
        if not text or not isinstance(text, str):
            return 0.5
            
        # 否定词列表
        negation_words = ['不', '非', '无', '没', '没有', '未', '勿', '别', '否', '并非']
        
        # 程度副词列表 - 格式：(副词, 权重)
        degree_adverbs = {
            '非常': 1.5, '很': 1.3, '极': 1.8, '极其': 1.8, '格外': 1.4,
            '分外': 1.4, '特别': 1.3, '尤其': 1.4, '更': 1.2, '更加': 1.2,
            '越': 1.2, '愈发': 1.2, '稍微': 0.8, '略微': 0.8, '有点': 0.9,
            '有些': 0.9, '较为': 0.9, '比较': 0.9, '相对': 0.9, '略': 0.8
        }
        
        # 负面组合词列表
        negative_phrase_list = [
            '增长放缓', '增速放缓', '失业率上升', '利润下降', '市场份额下降',
            '业绩下滑', '销量下滑', '收入下滑', '价格下跌', '股市下跌',
            '产品召回', '召回事件', '持续发酵', '股价大跌', '成本压力',
            '成本骤增', '价格上涨', '原材料上涨', '核心人员离职', '技术人员离职',
            '研发受挫', '项目受挫', '财务造假', '高管被调查', '供应链断裂'
        ]
        
        positive_score = 0
        negative_score = 0
        word_count = 0
        
        # 检查负面组合词
        for phrase in negative_phrase_list:
            if phrase in text:
                # 负面组合词权重
                negative_score += 3.0
        
        try:
            # 使用SnowNLP进行分词
            s = SnowNLP(text)
            words = s.words
            
            # 确保words是列表类型
            if not isinstance(words, list):
                words = []
        except Exception as e:
            # 分词失败时，使用空列表
            logger.error(f"分词失败: {e}")
            words = []
        
        # 标记是否遇到否定词
        negation_flag = False
        # 记录当前的程度副词权重
        degree_weight = 1.0
        
        for i, word in enumerate(words):
            word_count += 1
            
            # 跳过空词
            if not word:
                continue
            
            # 检查否定词
            if word in negation_words:
                negation_flag = True
                continue
            
            # 检查程度副词
            if word in degree_adverbs:
                degree_weight = degree_adverbs[word]
                continue
            
            # 检查正面词
            if word in self.positive_words:
                base_score = self.positive_words[word]
                # 应用程度副词权重
                adjusted_score = base_score * degree_weight
                # 如果遇到否定词，反转情感
                if negation_flag:
                    negative_score += adjusted_score
                    negation_flag = False  # 重置否定标记
                else:
                    positive_score += adjusted_score
                # 重置程度副词权重
                degree_weight = 1.0
            
            # 检查负面词
            elif word in self.negative_words:
                base_score = abs(self.negative_words[word])  # 取绝对值
                # 应用程度副词权重
                adjusted_score = base_score * degree_weight
                # 如果遇到否定词，反转情感
                if negation_flag:
                    positive_score += adjusted_score
                    negation_flag = False  # 重置否定标记
                else:
                    negative_score += adjusted_score
                # 重置程度副词权重
                degree_weight = 1.0
            
            # 检查中性词
            elif word in self._load_financial_neutral_words():
                negation_flag = False
                degree_weight = 1.0
            
            # 其他词，重置标记
            else:
                negation_flag = False
                degree_weight = 1.0
        
        # 如果单词数为0，返回中性得分
        if word_count == 0:
            return 0.5
        
        # 计算最终得分（负面得分减去正面得分）
        total_score = (positive_score - negative_score) / word_count
        
        # 将得分归一化到0-1之间
        # 调整归一化范围，考虑到否定词和程度副词的影响
        normalized_score = (total_score + 4) / 8
        
        return max(0.0, min(1.0, normalized_score))
    
    def _analyze_title_sentiment(self, title):
        """分析标题的情感，标题通常包含更强烈的情感倾向"""
        return self.analyze_sentiment(title)['sentiment_score']
    
    def analyze_news_sentiment(self, news_item):
        """分析单篇新闻的情感，标题权重更高"""
        try:
            # 分别分析标题和内容的情感
            title = news_item.title
            content = news_item.content
            
            # 标题情感分析
            title_result = self.analyze_sentiment(title)
            # 内容情感分析
            content_result = self.analyze_sentiment(content)
            
            # 标题权重更高（60%），内容权重更低（40%）
            final_score = (title_result['sentiment_score'] * 0.6) + (content_result['sentiment_score'] * 0.4)
            
            # 确保得分在0-1之间
            final_score = max(0.0, min(1.0, final_score))
            
            # 确定情感类型 - 使用与analyze_sentiment相同的阈值
            if final_score > 0.52:
                sentiment_type = '正面'
            elif final_score < 0.50:
                sentiment_type = '负面'
            else:
                sentiment_type = '中性'
            
            return {
                'sentiment_score': round(final_score, 4),
                'sentiment_type': sentiment_type,
                'title_score': round(title_result['sentiment_score'], 4),
                'content_score': round(content_result['sentiment_score'], 4),
                'snow_score': round((title_result['snow_score'] + content_result['snow_score']) / 2, 4),
                'financial_score': round((title_result['financial_score'] + content_result['financial_score']) / 2, 4)
            }
        except Exception as e:
            logger.error(f"分析新闻情感失败: {e}")
            return {
                'sentiment_score': 0.5,
                'sentiment_type': '中性',
                'title_score': 0.5,
                'content_score': 0.5,
                'snow_score': 0.5,
                'financial_score': 0.5
            }
    
    def analyze_batch_news(self, news_list):
        """批量分析新闻情感"""
        results = []
        for news in news_list:
            result = self.analyze_news_sentiment(news)
            results.append({
                'news_id': news.id,
                'title': news.title,
                **result
            })
        return results
    
    def analyze_from_database(self):
        """从数据库中读取新闻进行情感分析"""
        from news_analysis.models import News, SentimentAnalysis
        
        logger.info("开始从数据库中分析新闻情感")
        
        try:
            # 读取所有未进行情感分析的新闻 - 使用调试中验证的正确方式
            news_list = News.objects.filter(
                is_valid=True, 
                is_ad=False,
                sentiment__isnull=True
            )
            logger.info(f"找到 {news_list.count()} 条需要进行情感分析的新闻")
            
            analyzed_count = 0
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for news in news_list:
                # 分析新闻情感
                sentiment_result = self.analyze_news_sentiment(news)
                
                # 保存分析结果到数据库
                SentimentAnalysis.objects.create(
                    news=news,
                    sentiment_score=sentiment_result['sentiment_score'],
                    sentiment_type=sentiment_result['sentiment_type']
                )
                
                analyzed_count += 1
                
                # 统计情感类型
                if sentiment_result['sentiment_type'] == '正面':
                    positive_count += 1
                elif sentiment_result['sentiment_type'] == '负面':
                    negative_count += 1
                else:
                    neutral_count += 1
            
            logger.info(f"情感分析完成，共分析 {analyzed_count} 条新闻")
            logger.info(f"正面: {positive_count}, 负面: {negative_count}, 中性: {neutral_count}")
            
            return {
                'analyzed_count': analyzed_count,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count
            }
        except Exception as e:
            logger.error(f"从数据库中分析新闻情感失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'analyzed_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
    
    def get_sentiment_trend(self, days=7):
        """获取指定天数内的情感趋势
        
        Args:
            days: 统计天数，默认7天
            
        Returns:
            list: 每天的情感趋势数据
        """
        from news_analysis.models import News, SentimentAnalysis
        from django.utils.timezone import now
        
        try:
            # 获取当前日期（仅日期部分，不含时间）
            today = now().date()
            
            # 计算开始日期：days天前的日期
            start_date = today - timedelta(days=days-1)
            
            # 按日期分组统计情感趋势
            sentiment_trends = []
            
            for i in range(days):
                current_date = start_date + timedelta(days=i)
                next_date = current_date + timedelta(days=1)
                
                # 统计当天的新闻情感，确保包含整个日期范围（从零点到零点）
                sentiments = SentimentAnalysis.objects.filter(
                    news__publish_time__date=current_date
                )
                
                if sentiments.exists():
                    # 计算情感得分平均值
                    avg_score = sum(s.sentiment_score for s in sentiments) / sentiments.count()
                    
                    # 统计各情感类型数量
                    positive_count = sentiments.filter(sentiment_type='正面').count()
                    negative_count = sentiments.filter(sentiment_type='负面').count()
                    neutral_count = sentiments.filter(sentiment_type='中性').count()
                    
                    sentiment_trends.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'avg_score': round(avg_score, 4),
                        'positive_count': positive_count,
                        'negative_count': negative_count,
                        'neutral_count': neutral_count,
                        'total_count': sentiments.count()
                    })
                else:
                    # 即使没有新闻，也要添加该日期的记录，保持图表连续
                    sentiment_trends.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'avg_score': 0.5,  # 默认中性得分
                        'positive_count': 0,
                        'negative_count': 0,
                        'neutral_count': 0,
                        'total_count': 0
                    })
            
            return sentiment_trends
        except Exception as e:
            logger.error(f"获取情感趋势失败: {e}")
            return []
    
    def get_sentiment_distribution(self):
        """获取整体情感分布
        
        Returns:
            dict: 各情感类型的分布情况
        """
        from news_analysis.models import SentimentAnalysis
        
        try:
            total_count = SentimentAnalysis.objects.count()
            
            if total_count == 0:
                return {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0,
                    'total': 0
                }
            
            # 统计各情感类型数量
            positive_count = SentimentAnalysis.objects.filter(sentiment_type='正面').count()
            negative_count = SentimentAnalysis.objects.filter(sentiment_type='负面').count()
            neutral_count = SentimentAnalysis.objects.filter(sentiment_type='中性').count()
            
            return {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count,
                'total': total_count,
                'positive_ratio': round(positive_count / total_count * 100, 2),
                'negative_ratio': round(negative_count / total_count * 100, 2),
                'neutral_ratio': round(neutral_count / total_count * 100, 2)
            }
        except Exception as e:
            logger.error(f"获取情感分布失败: {e}")
            return {
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'total': 0
            }
