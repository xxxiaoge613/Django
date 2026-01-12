from .base_spider import BaseSpider
import logging
import requests
from bs4 import BeautifulSoup
import time
import xml.etree.ElementTree as ET
import asyncio
from crawl4ai import AsyncWebCrawler
from urllib.parse import urljoin
import re
import random
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

def retry(max_retries=3, delay=1, backoff=2):
    """
    重试装饰器
    :param max_retries: 最大重试次数
    :param delay: 初始延迟时间（秒）
    :param backoff: 延迟倍数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"函数 {func.__name__} 执行失败，已重试 {max_retries} 次，错误: {e}")
                        # 对于网络超时等异常，我们记录日志但不中断程序
                        if "timeout" in str(e).lower() or "connection" in str(e).lower():
                            logger.warning(f"网络相关错误，跳过当前操作继续执行...")
                            return None
                        raise e
                    
                    logger.warning(f"函数 {func.__name__} 执行失败，{current_delay} 秒后进行第 {retries} 次重试...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator

class ThirtySixKrSpider(BaseSpider):
    """36氪爬虫，支持RSS和Crawl4AI两种模式"""
    
    def __init__(self, max_pages=1, delay_range=(1, 3)):
        super().__init__(platform_name='36kr')
        self.base_url = 'https://36kr.com'
        # 配置RSS源，优先使用RSSHub链接
        self.rss_urls = [
            'https://rsshub.rssforever.com/36kr/news',  # RSSHub实例（优先使用）
            'https://36kr.com/feed'  # 官方RSS源作为备用    
        ]
        # Crawl4AI配置
        self.crawler_base_url = "https://36kr.com/information/web_news/"
        self.max_pages = max_pages  # 使用Crawl4AI时最大爬取页数
        self.delay_range = delay_range  # 随机延迟范围（秒）
    
    def _format_publish_time(self, time_str):
        """
        将相对时间转换为标准时间格式
        :param time_str: 原始时间字符串，如"1分钟前"、"2小时前"等
        :return: 标准时间格式的datetime对象
        """
        if not time_str:
            return self.parse_datetime("")
        
        # 清理字符串，移除不必要的字符
        time_str = time_str.strip().replace('\n', '').replace('\r', '')
        
        # 获取当前时间
        now = datetime.now()
        
        # 处理不同的时间格式
        if "分钟前" in time_str:
            minutes = re.search(r'(\d+)', time_str)
            if minutes:
                minutes = int(minutes.group(1))
                publish_time = now - timedelta(minutes=minutes)
                return self.parse_datetime(publish_time.strftime("%Y-%m-%d %H:%M"))
        elif "小时前" in time_str:
            hours = re.search(r'(\d+)', time_str)
            if hours:
                hours = int(hours.group(1))
                publish_time = now - timedelta(hours=hours)
                return self.parse_datetime(publish_time.strftime("%Y-%m-%d %H:%M"))
        elif "天前" in time_str:
            days = re.search(r'(\d+)', time_str)
            if days:
                days = int(days.group(1))
                publish_time = now - timedelta(days=days)
                return self.parse_datetime(publish_time.strftime("%Y-%m-%d %H:%M"))
        elif "昨天" in time_str:
            publish_time = now - timedelta(days=1)
            # 尝试提取具体时间
            time_part = re.search(r'(\d+:\d+)', time_str)
            if time_part:
                time_str_part = time_part.group(1)
                return self.parse_datetime(f"{publish_time.strftime('%Y-%m-%d')} {time_str_part}")
            else:
                return self.parse_datetime(publish_time.strftime("%Y-%m-%d %H:%M"))
        elif "前天" in time_str:
            publish_time = now - timedelta(days=2)
            # 尝试提取具体时间
            time_part = re.search(r'(\d+:\d+)', time_str)
            if time_part:
                time_str_part = time_part.group(1)
                return self.parse_datetime(f"{publish_time.strftime('%Y-%m-%d')} {time_str_part}")
            else:
                return self.parse_datetime(publish_time.strftime("%Y-%m-%d %H:%M"))
        elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', time_str):
            # 已经是标准格式
            return self.parse_datetime(time_str)
        elif re.match(r'\d{2}-\d{2} \d{2}:\d{2}', time_str):
            # 处理"10-14 09:27"格式
            return self.parse_datetime(f"2025-{time_str}")
        else:
            # 如果无法解析，返回当前时间
            return self.parse_datetime("")
    
    async def _scrape_page(self, crawler, url):
        """使用Crawl4AI爬取单个页面的文章信息"""
        try:
            result = await crawler.arun(url=url)
            
            # 检查爬取结果是否有效
            if not result or not result.html:
                logger.error(f"Crawl4AI爬取 {url} 未返回有效HTML内容")
                return [], False
            
            # 使用 BeautifulSoup 解析 HTML 内容
            try:
                soup = BeautifulSoup(result.html, 'html.parser')
            except Exception as parse_error:
                logger.error(f"解析页面 {url} 的HTML时出错: {parse_error}")
                return [], False
            
            # 查找文章列表容器 - 尝试多种可能的选择器
            article_container = soup.find('div', class_='information-flow-list')
            if not article_container:
                article_container = soup.find('div', id='information-flow-list')
            if not article_container:
                article_container = soup.find('div', class_='flow-list')
            if not article_container:
                article_container = soup.find('div', class_='kr-article-list')
            if not article_container:
                article_container = soup.find('div', class_='list-container')
            
            if not article_container:
                logger.warning(f"页面 {url} 未找到文章列表容器，可能页面结构已变化")
                logger.debug(f"页面 {url} 的HTML内容前500字符: {result.html[:500]}...")
                return [], False
                
            # 查找所有文章项 - 尝试多种可能的选择器
            articles = article_container.find_all('div', class_='information-flow-item')
            if not articles:
                articles = article_container.find_all('article', class_='information-flow-item')
            if not articles:
                articles = article_container.find_all('div', class_='flow-item')
            if not articles:
                articles = article_container.find_all('div', class_='kr-article-item')
            if not articles:
                articles = article_container.find_all('article', class_='article-item')
            
            if not articles:
                logger.warning(f"页面 {url} 找到文章列表容器但没有找到文章项，可能选择器已失效")
                logger.debug(f"文章列表容器HTML: {str(article_container)[:300]}...")
                return [], False
            
            # 存储所有文章信息
            articles_data = []
            
            # 遍历所有文章并提取信息
            for idx, article in enumerate(articles):
                try:
                    # 提取标题和链接 - 增加更多选择器
                    title_elem = article.find('a', class_='article-item-title')
                    if not title_elem:
                        title_elem = article.find('h2', class_='article-title').find('a') if article.find('h2', class_='article-title') else None
                    if not title_elem:
                        title_elem = article.find('a', href=re.compile(r'/p/\d+'))
                    if not title_elem:
                        title_elem = article.find('a', class_='title')
                    if not title_elem:
                        title_elem = article.find('h3').find('a') if article.find('h3') else None
                    
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    link = title_elem.get('href') if title_elem else ""
                    
                    # 处理相对链接
                    if link and not link.startswith('http'):
                        link = urljoin(url, link)
                    
                    # 提取发布时间 - 增加更多选择器
                    time_elem = article.find('span', class_='kr-flow-bar-time')
                    if not time_elem:
                        time_elem = article.find('span', class_='publish-time')
                    if not time_elem:
                        time_elem = article.find('time')
                    if not time_elem:
                        time_elem = article.find('span', class_='time')
                    if not time_elem:
                        time_elem = article.find('div', class_='article-meta').find('span') if article.find('div', class_='article-meta') else None
                    
                    publish_time_raw = time_elem.get_text(strip=True) if time_elem else ""
                    publish_time = self._format_publish_time(publish_time_raw)
                    
                    # 将文章信息添加到列表，确保有标题和链接
                    if title and link:
                        articles_data.append({
                            'title': title,
                            'link': link,
                            'publish_time': publish_time
                        })
                    else:
                        logger.debug(f"页面 {url} 第 {idx+1} 篇文章缺少标题或链接，跳过")
                        logger.debug(f"文章HTML: {str(article)[:300]}...")
                except Exception as e:
                    logger.error(f"页面 {url} 解析第 {idx+1} 篇文章时出错: {e}", exc_info=True)
                    logger.debug(f"文章HTML: {str(article)[:300]}...")
                    continue
            
            return articles_data, len(articles_data) > 0  # 返回数据和是否有内容的标志
        except Exception as e:
            logger.error(f"使用Crawl4AI爬取页面 {url} 时出错: {e}", exc_info=True)
            return [], False
    
    async def _scrape_all_articles(self):
        """使用Crawl4AI爬取所有页面的文章"""
        # 创建爬虫实例
        crawler = AsyncWebCrawler()
        
        try:
            # 启动爬虫
            await crawler.start()
            
            # 存储所有文章信息和已处理的链接（用于去重）
            all_articles_data = []
            seen_links = set()  # 用于跨页面去重
            page_num = 0
            total_saved = 0
            empty_page_count = 0  # 连续空页面计数
            max_empty_pages = 2  # 允许的最大连续空页面数
            
            # 循环爬取所有页面，直到没有更多内容或达到最大页数
            while page_num < self.max_pages and empty_page_count < max_empty_pages:
                # 构造页面URL
                if page_num == 0:
                    page_url = self.crawler_base_url
                else:
                    page_url = f"https://36kr.com/information/web_news/p/{page_num + 1}"
                
                logger.info(f"使用Crawl4AI爬取第 {page_num + 1} 页: {page_url}")
                
                # 尝试爬取页面，最多重试3次
                retry_count = 0
                max_retries = 3
                articles_data = []
                has_content = False
                
                while retry_count < max_retries:
                    try:
                        articles_data, has_content = await self._scrape_page(crawler, page_url)
                        if has_content:
                            break  # 成功获取内容，退出重试循环
                        else:
                            retry_count += 1
                            logger.warning(f"第 {page_num + 1} 页重试第 {retry_count} 次")
                            await asyncio.sleep(2 * retry_count)  # 指数退避
                    except Exception as e:
                        retry_count += 1
                        logger.error(f"第 {page_num + 1} 页第 {retry_count} 次重试失败: {e}")
                        await asyncio.sleep(2 * retry_count)  # 指数退避
                
                if not has_content:
                    empty_page_count += 1
                    logger.info(f"第 {page_num + 1} 页没有内容，连续空页面数: {empty_page_count}/{max_empty_pages}")
                    page_num += 1
                    continue
                else:
                    empty_page_count = 0  # 重置连续空页面计数
                
                logger.info(f"第 {page_num + 1} 页获取到 {len(articles_data)} 篇文章")
                
                # 去除跨页面的重复文章
                unique_page_articles = []
                for article in articles_data:
                    if article['link'] not in seen_links:
                        unique_page_articles.append(article)
                        seen_links.add(article['link'])
                
                if not unique_page_articles:
                    logger.info(f"第 {page_num + 1} 页的文章已全部处理过")
                    page_num += 1
                    continue
                
                logger.info(f"第 {page_num + 1} 页获取到 {len(unique_page_articles)} 篇新文章")
                
                # 处理每篇文章
                page_saved = 0
                for article in unique_page_articles:
                    try:
                        logger.info(f"处理文章: {article['title']}")
                        
                        # 从链接中提取source_id
                        try:
                            source_id = article['link'].split('/')[-1].split('.')[0] if '/' in article['link'] else article['link']
                            if not source_id:
                                source_id = article['link']  # 如果提取失败，使用完整链接作为source_id
                        except Exception as source_id_error:
                            logger.error(f"提取文章 {article['title']} 的source_id时出错: {source_id_error}")
                            source_id = article['link']  # 降级处理，使用完整链接作为source_id
                        
                        # 爬取新闻详情获取完整内容
                        content = None
                        try:
                            content = self._crawl_detail_content(article['link'])
                        except Exception as content_error:
                            logger.error(f"爬取文章 {article['title']} 的详情时出错: {content_error}")
                        
                        if not content or len(content.strip()) < 50:  # 内容过短也视为无效
                            logger.warning(f"文章 {article['title']} 内容为空或过短，跳过")
                            continue
                        
                        # 组装新闻数据 - 增加数据完整性检查
                        try:
                            news_data = {
                                'title': article['title'],
                                'content': content,
                                'publish_time': article['publish_time'],
                                'url': article['link'],
                                'platform': self.platform_name,
                                'source_id': source_id,
                                'author': '36氪',  # Crawl4AI中没有作者信息，默认为36氪
                                'read_count': 0,  # Crawl4AI中没有阅读量信息
                                'is_valid': True
                            }
                            
                            # 验证新闻数据的完整性
                            required_fields = ['title', 'content', 'url', 'source_id']
                            for field in required_fields:
                                if not news_data[field]:
                                    logger.warning(f"文章 {article['title']} 缺少必填字段 {field}，跳过")
                                    raise ValueError(f"缺少必填字段 {field}")
                            
                            # 保存到数据库
                            try:
                                self.save_to_database(news_data)
                                total_saved += 1
                                page_saved += 1
                            except Exception as db_error:
                                logger.error(f"保存文章 {article['title']} 到数据库时出错: {db_error}", exc_info=True)
                                continue
                        except Exception as data_error:
                            logger.error(f"组装文章 {article['title']} 数据时出错: {data_error}")
                            continue
                        
                        # 增加随机延迟，避免请求过于频繁
                        delay = random.uniform(*self.delay_range)
                        time.sleep(delay)
                        logger.debug(f"延迟 {delay:.2f} 秒后继续处理下一篇文章")
                        
                    except Exception as e:
                        logger.error(f"处理文章失败: {article.get('title', '未知标题')} - {e}", exc_info=True)
                        continue
                
                logger.info(f"第 {page_num + 1} 页成功保存 {page_saved} 条记录到数据库")
                
                # 将当前页面的文章添加到总列表中
                all_articles_data.extend(unique_page_articles)
                
                page_num += 1
                
                # 在页面之间添加随机延时
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
                logger.debug(f"延迟 {delay:.2f} 秒后爬取下一页")
            
            logger.info(f"Crawl4AI爬取结束，总共处理了 {page_num} 个页面，获取到 {len(all_articles_data)} 篇文章，成功保存 {total_saved} 条记录到数据库")
            
            return all_articles_data
            
        except Exception as e:
            logger.error(f"Crawl4AI抓取过程中出现错误: {e}", exc_info=True)
            return []
        finally:
            # 关闭爬虫
            try:
                await crawler.close()
            except Exception as e:
                logger.error(f"关闭爬虫失败: {e}")
    
    def crawl_news_list_crawl4ai(self):
        """使用Crawl4AI爬取36氪新闻列表"""
        try:
            asyncio.run(self._scrape_all_articles())
        except Exception as e:
            logger.error(f"Crawl4AI爬取失败: {e}")
    
    def crawl_news_list(self, page=1, use_crawl4ai=False):
        """爬取36氪新闻列表，支持RSS和Crawl4AI两种模式
        
        Args:
            page: 爬取的页码（仅对RSS模式有效）
            use_crawl4ai: 是否使用Crawl4AI模式代替RSS
        """
        if use_crawl4ai:
            return self.crawl_news_list_crawl4ai()
        for i, rss_url in enumerate(self.rss_urls):
            try:
                logger.info(f"开始抓取36kr RSS feed (源 {i+1}/{len(self.rss_urls)}): {rss_url}")
                
                # 获取RSS内容
                response = requests.get(rss_url, timeout=30)  # 增加超时时间到30秒
                response.raise_for_status()  # 检查请求是否成功
                
                # 解析RSS - 使用标准库xml.etree.ElementTree
                root = ET.fromstring(response.text)
                
                # 根据RSS源类型选择不同的解析方法
                if "rsshub.rssforever.com" in rss_url:
                    # RSSHub源处理逻辑
                    items = self._parse_rsshub_items(root)
                else:
                    # 36kr.com/feed源处理逻辑
                    items = self._parse_36kr_feed_items(root)
                
                logger.info(f"获取到 {len(items)} 篇文章")
                
                # 处理每篇文章
                for item in items:
                    try:
                        # 获取文章基本信息 - 不依赖特定命名空间
                        title = ''
                        link = ''
                        pub_date = ''
                        description = ''
                        
                        for child in item:
                            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                            
                            if tag == 'title':
                                title = child.text.strip() if child.text else ''
                            if tag == 'link':
                                link = child.text if child.text else ''
                            if tag == 'pubDate':
                                pub_date = child.text if child.text else ''
                            if tag == 'description':
                                description = child.text if child.text else ''
                        
                        if not title or not link:
                            continue
                        
                        # 解析发布时间
                        publish_time = self.parse_datetime(pub_date)
                        
                        logger.info(f"处理文章: {title}")
                        
                        # 从链接中提取source_id
                        source_id = link.split('/')[-1].split('.')[0] if '/' in link else link
                        
                        # 爬取新闻详情获取完整内容
                        content = self._extract_content_from_html(description)
                        if not content:
                            # 如果描述中没有完整内容，尝试爬取详情页
                            content = self._crawl_detail_content(link)
                        
                        # 组装新闻数据
                        news_data = {
                            'title': title,
                            'content': content,
                            'publish_time': publish_time,
                            'url': link,
                            'platform': self.platform_name,
                            'source_id': source_id,
                            'author': '36氪',  # RSS中没有作者信息，默认为36氪
                            'read_count': 0,  # RSS中没有阅读量信息
                            'is_valid': True
                        }
                        
                        # 保存到数据库
                        self.save_to_database(news_data)
                        
                        # 增加随机延迟，避免请求过于频繁
                        delay = random.uniform(*self.delay_range)
                        time.sleep(delay)
                        logger.debug(f"延迟 {delay:.2f} 秒后继续处理下一篇文章")
                        
                    except Exception as e:
                        logger.error(f"处理文章失败: {title} - {e}", exc_info=True)
                        continue
                
                logger.info(f"36kr RSS feed 抓取完成，共处理 {len(items)} 篇文章")
                return  # 如果成功，直接返回
                
            except requests.RequestException as e:
                logger.error(f"请求RSS源 {i+1} 失败: {e}", exc_info=True)
                # 继续尝试下一个源
                continue
            except ET.ParseError as e:
                logger.error(f"解析RSS源 {i+1} 失败: {e}", exc_info=True)
                # 继续尝试下一个源
                continue
            except Exception as e:
                logger.error(f"处理RSS源 {i+1} 失败: {e}", exc_info=True)
                # 继续尝试下一个源
                continue
        
        logger.error(f"所有RSS源都尝试失败，自动切换到Crawl4AI模式")
        # 所有RSS源都失败，自动切换到Crawl4AI模式
        return self.crawl_news_list_crawl4ai()
    
    def _extract_content_from_html(self, html_content):
        """从HTML描述中提取正文内容，保留图片标签"""
        if not html_content:
            return ''
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # 移除所有脚本和样式
            for script in soup(['script', 'style']):
                script.decompose()
            
            # 提取文本和图片
            content = []
            
            # 获取所有需要的标签，不使用descendants避免获取多余内容
            text_elements = soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img'])
            
            for elem in text_elements:
                if elem.name == 'img':
                    # 保留图片标签
                    img_src = elem.get('src')
                    if img_src:
                        content.append(f'<img src="{img_src}" alt="图片" class="news-img" />')
                else:
                    # 提取段落文本
                    text = elem.get_text(strip=True)
                    if text:
                        content.append(f'<{elem.name}>{text}</{elem.name}>')
            
            return '\n'.join(content)
        except Exception as e:
            logger.error(f"提取内容失败: {e}")
            return ''
    
    def _parse_rsshub_items(self, root):
        """解析RSSHub源的items元素"""
        items = []
        for elem in root.iter():
            if elem.tag.endswith('item') or elem.tag == 'item':
                items.append(elem)
        return items
    
    def _parse_36kr_feed_items(self, root):
        """解析36kr.com/feed源的items元素"""
        items = []
        # 36kr.com/feed使用标准RSS 2.0格式，没有复杂命名空间
        for channel in root.findall('channel'):
            for item in channel.findall('item'):
                items.append(item)
        return items
    
    @retry(max_retries=3, delay=2, backoff=2)
    def _crawl_detail_content(self, url):
        """爬取详情页内容，保留图片标签"""
        try:
            logger.info(f"爬取详情页: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找主要内容区域
            content = ''
            content_tags = soup.find_all(['div', 'article'], class_=lambda x: x and (
                'article-content' in x or 
                'articleDetail-content' in x or 
                'content' in x or 
                'post-content' in x or 
                'main-content' in x
            ))
            
            if content_tags:
                best_content_tag = None
                max_p_count = 0
                
                for tag in content_tags:
                    p_count = len(tag.find_all('p'))
                    if p_count > max_p_count:
                        max_p_count = p_count
                        best_content_tag = tag
                
                if not best_content_tag:
                    best_content_tag = content_tags[0]
                
                # 提取文本和图片
                content_parts = []
                
                # 获取所有需要的标签，不使用descendants避免获取下一篇
                text_elements = best_content_tag.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'img'])
                
                for elem in text_elements:
                    if elem.name == 'img':
                        # 保留图片标签
                        img_src = elem.get('src')
                        if img_src:
                            content_parts.append(f'<img src="{img_src}" alt="图片" class="news-img" />')
                    else:
                        # 提取段落文本
                        text = elem.get_text(strip=True, separator=' ')
                        if text and len(text) > 10:
                            content_parts.append(f'<{elem.name}>{text}</{elem.name}>')
                
                content = '\n'.join(content_parts)
            
            # 清理内容
            if content:
                import re
                filter_patterns = [
                    r'本文来自微信公众号.*?36氪经授权发布',
                    r'该文观点仅代表作者本人.*?36氪平台仅提供信息存储空间服务',
                    r'TA没有写简介，但内敛也是一种表达',
                    r'\*\*.*?\*\*',  # 过滤加粗标记
                    r'\d{4}年\d{1,2}月\d{1,2}日.*?\d{1,2}:\d{2}',  # 过滤时间戳
                    r'来源：.*?36氪',  # 过滤来源
                    r'作者：.*?36氪',  # 过滤作者
                    r'责任编辑：.*?',  # 过滤责任编辑
                    r'版权声明：.*?',  # 过滤版权声明
                    r'转载请注明出处：.*?',  # 过滤转载声明
                    r'相关阅读推荐：.*?',  # 过滤相关阅读
                    r'延伸阅读：.*?',  # 过滤延伸阅读
                    r'本文仅供参考.*?',  # 过滤免责声明
                    r'风险提示：.*?',  # 过滤风险提示
                    r'更多精彩内容请关注.*?',  # 过滤关注提示
                    r'下载36氪APP.*?',  # 过滤APP推广
                    r'加入36氪会员.*?',  # 过滤会员推广
                    r'扫描二维码.*?',  # 过滤二维码提示
                    r'广告合作：.*?',  # 过滤广告合作
                    r'商务合作：.*?',  # 过滤商务合作
                    r'联系方式：.*?'  # 过滤联系方式
                ]
                
                for pattern in filter_patterns:
                    content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
                
                content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
            
            return content
        except Exception as e:
            logger.error(f"爬取详情页失败: {url} - {e}")
            return ''
    
    def crawl_news_detail(self, news_url, basic_info):
        """爬取36氪新闻详情 - 兼容原有接口"""
        try:
            content = self._crawl_detail_content(news_url)
            
            # 组装新闻数据
            news_data = {
                'title': basic_info['title'],
                'content': content,
                'publish_time': basic_info['publish_time'],
                'url': news_url,
                'platform': self.platform_name,
                'source_id': news_url.split('/')[-1].split('.')[0] if '/' in news_url else news_url,
                'author': basic_info['author'] if 'author' in basic_info else '36氪',
                'read_count': 0,
                'is_valid': True,
                'is_ad': False
            }
            
            # 保存到数据库
            self.save_to_database(news_data)
        except Exception as e:
            logger.error(f"爬取新闻详情失败: {news_url} - {e}", exc_info=True)
