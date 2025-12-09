from .base_spider import BaseSpider
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class QuantumBitSpider(BaseSpider):
    """量子位爬虫"""
    
    def __init__(self):
        super().__init__(platform_name='量子位')
        self.base_url = 'https://www.qbitai.com'
    
    def crawl_news_list(self, page=1, max_pages=5):
        """爬取量子位财经新闻列表
        
        Args:
            page: 当前页码
            max_pages: 最大爬取页数，防止无限递归
        """
        try:
            # 检查是否超过最大爬取页数
            if page > max_pages:
                logger.info(f"已达到最大爬取页数 {max_pages}，停止爬取")
                return
            
            # 使用用户提供的财经分类URL
            url = f'{self.base_url}/category/%e8%b5%84%e8%ae%af?page={page}'
            logger.info(f"开始爬取量子位财经新闻列表，页码: {page}/{max_pages}")
            
            # 使用新的请求方法
            response = self._make_request(url)
            if not response:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻列表项 - 尝试多种选择器
            logger.info("尝试查找新闻列表元素...")
            
            # 尝试多种新闻列表选择器，根据量子位网站实际结构优化
            news_selectors = [
                'div.picture_text',
                'article.post',
                'div.article-item',
                'div.post-item',
                'div.main-container div.picture_text',
                'div#primary div.picture_text',
                'div.content-wrapper div.picture_text'
            ]
            
            news_items = []
            for selector in news_selectors:
                found_items = soup.select(selector)
                logger.info(f"使用选择器 '{selector}' 找到 {len(found_items)} 条新闻")
                if found_items:
                    news_items = found_items
                    break
            
            logger.info(f"最终找到 {len(news_items)} 条新闻")
            
            for item in news_items:
                try:
                    # 解析新闻标题和链接
                    title_tag = None
                    
                    # 尝试多种标题选择器
                    title_selectors = [
                        'h4 > a',
                        'h2 > a',
                        'h3 > a',
                        'a.title',
                        'a[title]'
                    ]
                    
                    for selector in title_selectors:
                        found_tag = item.select_one(selector)
                        if found_tag and found_tag.text.strip():
                            title_tag = found_tag
                            break
                    
                    if not title_tag:
                        # 如果找不到，尝试查找所有a标签
                        a_tags = item.find_all('a')
                        for a in a_tags:
                            if a.text.strip() and len(a.text.strip()) > 5:
                                title_tag = a
                                break
                    
                    if not title_tag:
                        continue
                    
                    # 提取标题和链接
                    title = title_tag.text.strip()
                    if not title or len(title) < 5:
                        continue
                    
                    news_url = title_tag.get('href')
                    if not news_url:
                        continue
                    
                    # 处理相对链接
                    if not news_url.startswith('http'):
                        if news_url.startswith('/'):
                            news_url = f'{self.base_url}{news_url}'
                        else:
                            news_url = f'{self.base_url}/{news_url}'
                    
                    # 解析发布时间和作者
                    author = '未知'
                    publish_time = self.parse_datetime('')
                    
                    # 尝试多种信息选择器
                    info_selectors = [
                        'div.info',
                        'div.post-meta',
                        'div.meta',
                        'span.author',
                        'span.time'
                    ]
                    
                    # 查找作者
                    author_tags = item.select('span.author, div.author, a[rel="author"]')
                    if author_tags:
                        author = author_tags[0].text.strip().replace('作者:', '').replace('by', '').strip()
                    
                    # 查找发布时间
                    time_tags = item.select('span.time, time, div.time, span.post-date')
                    if time_tags:
                        time_text = time_tags[0].text.strip().replace('发布于', '').replace('Posted on', '').strip()
                        publish_time = self.parse_datetime(time_text)
                    
                    logger.info(f"解析到新闻: {title[:50]}..., 链接: {news_url}, 作者: {author}, 时间: {publish_time}")
                    
                    # 检查新闻是否已存在，避免重复爬取详情页
                    from news_analysis.models import News
                    import django.db.models as models
                    
                    # 生成source_id，用于检查新闻是否存在
                    source_id = news_url.split('/')[-1] if '/' in news_url else news_url
                    if '.' in source_id:
                        source_id = source_id.split('.')[0]
                    
                    # 检查是否已存在相同的新闻（通过url或source_id去重）
                    existing_news = News.objects.filter(
                        models.Q(url=news_url) | models.Q(source_id=source_id)
                    ).first()
                    
                    if existing_news:
                        logger.info(f"新闻已存在，跳过详情页爬取: {title[:50]}...")
                        continue
                    
                    # 爬取新闻详情
                    self.crawl_news_detail(news_url, {
                        'title': title,
                        'publish_time': publish_time,
                        'author': author
                    })
                except Exception as e:
                    logger.error(f"解析新闻列表项失败: {e}")
                    continue
            
            # 量子位网站没有明显的下一页链接，直接使用URL分页机制
            next_page_num = page + 1
            if next_page_num <= max_pages:
                logger.info(f"准备爬取下一页，页码: {next_page_num}/{max_pages}")
                self.crawl_news_list(next_page_num, max_pages)
            else:
                logger.info(f"已达到最大爬取页数 {max_pages}，停止爬取")
        except Exception as e:
            logger.error(f"爬取量子位新闻列表失败: {e}")
            import traceback
            traceback.print_exc()
    
    def crawl_news_detail(self, news_url, basic_info):
        """爬取量子位新闻详情"""
        try:
            logger.info(f"开始爬取新闻详情: {news_url}")
            
            # 详情页爬取额外增加3-5秒等待时间
            import random
            import time
            detail_delay = random.uniform(3, 5)
            logger.info(f"详情页额外等待: {detail_delay}秒")
            time.sleep(detail_delay)
            
            # 使用带反爬措施的请求方法
            response = self._make_request(news_url)
            if not response:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析新闻内容 - 尝试多种选择器，保留段落结构
            content = ''
            
            # 尝试更多的内容选择器，优先使用用户提供的选择器
            content_selectors = [
                'body > div.main > div.content > div.article',
                'div.article-content',
                'div.entry-content',
                'article.post',
                'div.single-post-content',
                'div.content',
                'div.main-content',
                'div.post-content',
                'div.news-content',
                'div.prose',
                'main article',
                'div.article-body',
                'div.content-wrapper'
            ]
            
            for selector in content_selectors:
                content_tag = soup.select_one(selector)
                if content_tag:
                    # 提取正文内容，保留段落结构
                    paragraphs = content_tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                    if paragraphs:
                        # 过滤掉广告和无效内容，保留有意义的段落
                        valid_paragraphs = []
                        for p in paragraphs:
                            text = p.text.strip()
                            # 过滤条件：长度大于10，不包含广告关键词
                            ad_keywords = ['广告', '推广', '赞助商', '点击查看', '阅读原文']
                            if text and len(text) > 10 and not any(keyword in text for keyword in ad_keywords):
                                valid_paragraphs.append(text)
                        content = '\n'.join(valid_paragraphs)
                    else:
                        # 如果没有找到特定标签，尝试按逻辑分割文本
                        import re
                        text = content_tag.text.strip()
                        # 按句号、问号、感叹号等分割成段落
                        paragraphs = re.split(r'(?<=[。！？\.!?])\s*', text)
                        if len(paragraphs) > 1:
                            valid_paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 10]
                            content = '\n'.join(valid_paragraphs)
                        else:
                            content = text
                    break
            
            # 如果还是没有内容，尝试查找所有p标签，按父元素分组
            if not content or len(content) < 100:
                # 查找所有p标签，按父元素分组
                all_p_tags = soup.find_all('p')
                if all_p_tags:
                    # 按父元素分组，找到p标签最多的父元素
                    parent_groups = {}
                    for p in all_p_tags:
                        parent = p.parent
                        parent_id = id(parent)
                        if parent_id not in parent_groups:
                            parent_groups[parent_id] = []
                        parent_groups[parent_id].append(p)
                    
                    # 找到p标签最多的组
                    if parent_groups:
                        largest_group = max(parent_groups.values(), key=len)
                        if len(largest_group) > 2:  # 至少3个p标签才视为正文
                            # 过滤掉短段落和无效内容
                            valid_paragraphs = []
                            for p in largest_group:
                                text = p.text.strip()
                                if text and len(text) > 20:
                                    valid_paragraphs.append(text)
                            content = '\n'.join(valid_paragraphs)
            
            # 清理内容，去除多余空行
            if content:
                # 去除连续空行，只保留一行
                content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
                paragraph_count = content.count('\n') + 1
                logger.info(f"成功提取量子位正文内容，长度: {len(content)}, 段落数: {paragraph_count}")
            else:
                logger.warning(f"无法提取量子位正文内容: {news_url}")
            
            # 解析阅读量
            read_count = 0
            read_selectors = [
                'span.read-count',
                'span.view-count',
                'div.post-views',
                'span.post-meta-item.post-views',
                'span.views',
                'span.reads'
            ]
            
            for selector in read_selectors:
                read_tag = soup.select_one(selector)
                if read_tag:
                    try:
                        read_text = read_tag.text.strip()
                        # 提取数字
                        import re
                        read_match = re.search(r'\d+', read_text)
                        if read_match:
                            read_count = int(read_match.group())
                        break
                    except:
                        continue
            
            # 生成source_id（使用url的最后部分，确保唯一性）
            source_id = news_url.split('/')[-1] if '/' in news_url else news_url
            if '.' in source_id:
                source_id = source_id.split('.')[0]
            
            # 确保source_id不为空
            if not source_id:
                source_id = str(self.request_count) + '_' + str(int(time.time()))
            
            logger.info(f"详情解析结果: 标题 {basic_info['title'][:30]}..., 内容长度 {len(content)}, 阅读量 {read_count}")
            
            # 组装新闻数据
            news_data = {
                'title': basic_info['title'],
                'content': content,
                'publish_time': basic_info['publish_time'],
                'url': news_url,
                'platform': self.platform_name,
                'source_id': source_id,
                'author': basic_info['author'],
                'read_count': read_count,
                'is_valid': len(content) > 100  # 只有内容长度超过100才视为有效
            }
            
            # 保存到数据库
            self.save_to_database(news_data)
        except Exception as e:
            logger.error(f"爬取新闻详情失败: {e}")
            import traceback
            traceback.print_exc()
