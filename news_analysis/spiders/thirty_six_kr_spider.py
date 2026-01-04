from .base_spider import BaseSpider
import logging
import requests
from bs4 import BeautifulSoup
import time
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class ThirtySixKrSpider(BaseSpider):
    """36氪爬虫，使用RSS获取新闻数据"""
    
    def __init__(self):
        super().__init__(platform_name='36kr')
        self.base_url = 'https://36kr.com'
        # 配置多个RSS源，优先尝试RSSHub链接
        self.rss_urls = [
            'https://rsshub.rssforever.com/36kr/news',  # RSSHub实例
            'https://36kr.com/feed'  # 原始RSS链接作为fallback
        ]
        # 当前使用的RSS源索引
        self.current_rss_index = 0
    
    def crawl_news_list(self, page=1):
        """爬取36氪新闻列表"""
        for i, rss_url in enumerate(self.rss_urls):
            try:
                logger.info(f"开始抓取36kr RSS feed (源 {i+1}/{len(self.rss_urls)}): {rss_url}")
                
                # 获取RSS内容
                response = requests.get(rss_url, timeout=10)
                response.raise_for_status()  # 检查请求是否成功
                
                # 解析RSS - 使用标准库xml.etree.ElementTree
                root = ET.fromstring(response.text)
                
                # 查找所有item元素
                items = []
                for elem in root.iter():
                    if elem.tag.endswith('item') or elem.tag == 'item':
                        items.append(elem)
                
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
                            if child.tag.endswith('title') or child.tag == 'title':
                                title = child.text.strip() if child.text else ''
                            if child.tag.endswith('link') or child.tag == 'link':
                                link = child.text if child.text else ''
                            if child.tag.endswith('pubDate') or child.tag == 'pubDate':
                                pub_date = child.text if child.text else ''
                            if child.tag.endswith('description') or child.tag == 'description':
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
                        
                        # 增加延迟，避免请求过于频繁
                        time.sleep(1)  # 1秒延迟
                        
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
        
        logger.error(f"所有RSS源都尝试失败")
    
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
            
            # 处理所有元素
            for elem in soup.descendants:
                if elem.name == 'img':
                    # 保留图片标签
                    img_src = elem.get('src')
                    if img_src:
                        content.append(f'<img src="{img_src}" alt="图片" class="news-img" />')
                elif elem.name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # 提取段落文本
                    text = elem.get_text(strip=True)
                    if text:
                        content.append(f'<{elem.name}>{text}</{elem.name}>')
            
            return '\n'.join(content)
        except Exception as e:
            logger.error(f"提取内容失败: {e}")
            return ''
    
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
                
                # 处理所有元素
                for elem in best_content_tag.descendants:
                    if elem.name == 'img':
                        # 保留图片标签
                        img_src = elem.get('src')
                        if img_src:
                            content_parts.append(f'<img src="{img_src}" alt="图片" class="news-img" />')
                    elif elem.name in ['p', 'h2', 'h3', 'h4', 'h5', 'h6']:
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
