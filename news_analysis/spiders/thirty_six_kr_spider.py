from .base_spider import BaseSpider
from bs4 import BeautifulSoup
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class ThirtySixKrSpider(BaseSpider):
    """36氪爬虫，使用playwright进行动态网页爬取"""
    
    def __init__(self):
        super().__init__(platform_name='36kr')
        self.base_url = 'https://36kr.com'
        self.playwright = None
        self.browser = None
        self.page = None
    
    def _ensure_playwright_initialized(self):
        """确保playwright已初始化"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
        if not self.browser:
            self.browser = self.playwright.chromium.launch(
                headless=True,  # 启用无头模式
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
        if not self.page:
            self.page = self.browser.new_page()
    
    def close(self):
        """关闭爬虫资源，使用更可靠的方式确保资源释放"""
        import threading
        import time
        
        def _safe_close():
            """安全关闭资源的内部函数"""
            try:
                # 先关闭页面
                if hasattr(self, 'page') and self.page:
                    try:
                        self.page.close()
                        self.page = None
                        logger.info("已关闭页面实例")
                    except Exception as e:
                        logger.error(f"关闭页面失败: {e}")
                        # 强制设置为None，避免后续操作
                        self.page = None
                
                # 再关闭浏览器 - 使用超时机制
                if hasattr(self, 'browser') and self.browser:
                    try:
                        # 使用线程方式调用browser.close()，避免阻塞
                        browser_thread = threading.Thread(
                            target=self.browser.close,
                            daemon=True
                        )
                        browser_thread.start()
                        # 等待最多5秒
                        browser_thread.join(timeout=5.0)
                        if browser_thread.is_alive():
                            logger.error("关闭浏览器超时，强制释放资源")
                        else:
                            logger.info("已关闭浏览器实例")
                    except Exception as e:
                        logger.error(f"关闭浏览器失败: {e}")
                    finally:
                        # 强制设置为None，避免后续操作
                        self.browser = None
                
                # 最后停止playwright
                if hasattr(self, 'playwright') and self.playwright:
                    try:
                        self.playwright.stop()
                        self.playwright = None
                        logger.info("已停止playwright")
                    except Exception as e:
                        logger.error(f"停止playwright失败: {e}")
                    finally:
                        # 强制设置为None，避免后续操作
                        self.playwright = None
                
                logger.info(f"{self.platform_name} 爬虫资源已完全关闭")
            except Exception as e:
                logger.error(f"安全关闭资源失败: {e}")
        
        try:
            # 启动一个新线程来关闭资源，避免阻塞主线程
            close_thread = threading.Thread(
                target=_safe_close,
                daemon=True
            )
            close_thread.start()
            
            # 等待资源关闭，最多10秒
            close_thread.join(timeout=10.0)
            
            if close_thread.is_alive():
                logger.error("资源关闭线程超时，程序将强制退出")
            
        except Exception as e:
            logger.error(f"启动资源关闭线程失败: {e}")
        finally:
            # 调用父类的close方法，使用try-except避免阻塞
            try:
                super().close()
            except Exception as e:
                logger.error(f"调用父类close方法失败: {e}")
    
    def crawl_news_list(self, page=1):
        """爬取36氪新闻列表"""
        try:
            self._ensure_playwright_initialized()
            # 使用用户提供的URL
            url = f'{self.base_url}/information/web_news/'
            logger.info(f"开始爬取36氪新闻列表，页码: {page}")
            
            # 使用playwright访问页面
            self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            logger.info(f"页面DOM加载成功")
            
            # 等待页面加载完成
            self.page.wait_for_timeout(2000)
            logger.info(f"页面加载完成")
            
            # 获取页面标题
            title = self.page.title()
            logger.info(f"页面标题: {title}")
            
            # 模拟滚动加载更多内容
            logger.info(f"开始模拟滚动加载...")
            for i in range(1):  # 只滚动1次，减少爬取数据量
                logger.info(f"执行第 {i+1} 次滚动")
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self.page.wait_for_timeout(2000)
            logger.info(f"滚动加载完成")
            
            # 获取页面HTML
            logger.info(f"开始获取页面HTML...")
            html = self.page.content()
            logger.info(f"页面HTML获取成功，长度: {len(html)}")
            
            # 保存HTML到文件，便于调试
            with open('36kr_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"HTML已保存到文件: 36kr_debug.html")
            
            soup = BeautifulSoup(html, 'html.parser')
            logger.info(f"HTML解析成功")
            
            # 查找所有新闻项容器
            news_items = soup.find_all('div', class_='information-flow-item')
            logger.info(f"找到 {len(news_items)} 条新闻")
            
            for item in news_items:
                try:
                    # 检查是否为广告新闻（商业策划）
                    is_ad = False
                    ad_tag = item.find('span', class_='kr-ad-logo')
                    if ad_tag and ad_tag.text.strip() == '商业策划':
                        logger.info(f"识别到广告新闻")
                        is_ad = True
                    
                    if is_ad:
                        # 广告新闻处理
                        ad_link_tag = item.find('a', sensors_operate_type='click')
                        if ad_link_tag:
                            # 广告新闻，记录基本信息
                            title = "广告新闻"
                            img_tag = ad_link_tag.find('img')
                            if img_tag and 'alt' in img_tag:
                                title = img_tag['alt'].strip()
                            news_url = ad_link_tag['href']
                            
                            # 广告新闻不需要爬取详情，直接保存
                            news_data = {
                                'title': title,
                                'content': '',
                                'publish_time': self.parse_datetime(''),
                                'url': news_url,
                                'platform': self.platform_name,
                                'source_id': news_url.split('/')[-1].split('.')[0] if '/' in news_url else news_url,
                                'author': '广告',
                                'read_count': 0,
                                'is_valid': True,
                                'is_ad': True
                            }
                            self.save_to_database(news_data)
                            continue
                    else:
                        # 正常新闻处理
                        # 查找kr-flow-article-item
                        article_item = item.find('div', class_='kr-flow-article-item')
                        if not article_item:
                            logger.warning(f"未找到正常新闻容器: {item}")
                            continue
                        
                        # 解析新闻标题和链接
                        title_wrapper = article_item.find('p', class_='title-wrapper')
                        if not title_wrapper:
                            continue
                        
                        title_tag = title_wrapper.find('a', class_='article-item-title')
                        if not title_tag:
                            continue
                        
                        title = title_tag.text.strip()
                        news_url = title_tag['href']
                        if not news_url.startswith('http'):
                            news_url = f'{self.base_url}{news_url}'
                        
                        # 解析发布时间和作者
                        kr_flow_bar = article_item.find('div', class_='kr-flow-bar')
                        if kr_flow_bar:
                            # 解析作者
                            author_tag = kr_flow_bar.find('a', class_='kr-flow-bar-author')
                            author = author_tag.text.strip() if author_tag else '未知'
                            
                            # 解析发布时间
                            time_tag = kr_flow_bar.find('span', class_='kr-flow-bar-time')
                            if time_tag:
                                time_text = time_tag.text.strip()
                                publish_time = self.parse_datetime(time_text)
                            else:
                                publish_time = self.parse_datetime('')
                        else:
                            publish_time = self.parse_datetime('')
                            author = '未知'
                        
                        # 爬取新闻详情
                        self.crawl_news_detail(news_url, {
                            'title': title,
                            'publish_time': publish_time,
                            'author': author
                        })
                except Exception as e:
                    logger.error(f"解析新闻列表项失败: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"爬取36氪新闻列表失败: {e}", exc_info=True)
        finally:
            # 确保资源释放
            self.close()
    
    def crawl_news_detail(self, news_url, basic_info):
        """爬取36氪新闻详情"""
        try:
            self._ensure_playwright_initialized()
            logger.info(f"开始爬取新闻详情: {news_url}")
            
            # 使用playwright访问详情页
            self.page.goto(news_url, wait_until='domcontentloaded', timeout=60000)
            logger.info(f"详情页DOM加载成功")
            
            # 等待内容加载 - 调整为3-5秒随机等待
            import random
            wait_time = random.uniform(3000, 5000)  # 毫秒
            logger.info(f"详情页内容加载等待: {wait_time/1000:.1f}秒")
            self.page.wait_for_timeout(wait_time)
            logger.info(f"详情页内容加载完成")
            
            # 获取页面HTML
            html = self.page.content()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 解析新闻内容 - 根据36氪网站结构调整，保留段落结构和强调内容
            content = ''
            
            # 查找主要内容区域
            content_tags = soup.find_all(['div', 'article'], class_=lambda x: x and (
                'article-content' in x or 
                'articleDetail-content' in x or 
                'content' in x or 
                'post-content' in x or 
                'main-content' in x
            ))
            
            if content_tags:
                # 选择最有可能是正文的内容区域（通常是第一个或包含p标签最多的）
                best_content_tag = None
                max_p_count = 0
                
                for tag in content_tags:
                    p_count = len(tag.find_all('p'))
                    if p_count > max_p_count:
                        max_p_count = p_count
                        best_content_tag = tag
                
                if not best_content_tag:
                    best_content_tag = content_tags[0]
                
                # 提取所有有意义的文本元素，保留HTML标签中的强调内容
                text_elements = best_content_tag.find_all(['p', 'h2', 'h3', 'h4'])
                if text_elements:
                    # 过滤掉短段落和无效内容
                    valid_paragraphs = []
                    for elem in text_elements:
                        # 保留标签内的文本，特别是strong标签的内容
                        text = elem.get_text(strip=True, separator=' ')
                        if text and len(text) > 10:
                            # 保留段落结构
                            valid_paragraphs.append(text)
                    content = '\n'.join(valid_paragraphs)
                else:
                    # 如果没有找到特定标签，尝试按逻辑分割文本
                    import re
                    text = best_content_tag.get_text(strip=True, separator=' ')
                    # 按句号、问号、感叹号等分割成段落
                    paragraphs = re.split(r'(?<=[。！？\.!?])\s*', text)
                    if len(paragraphs) > 1:
                        valid_paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 10]
                        content = '\n'.join(valid_paragraphs)
                    else:
                        content = text
            
            # 如果还是没有内容，尝试查找所有p标签
            if not content or len(content) < 100:
                all_paragraphs = soup.find_all('p')
                if all_paragraphs:
                    # 过滤掉短段落和无效内容
                    valid_paragraphs = []
                    for p in all_paragraphs:
                        text = p.get_text(strip=True, separator=' ')
                        if text and len(text) > 20:
                            valid_paragraphs.append(text)
                    content = '\n'.join(valid_paragraphs)
            
            # 清理内容，去除多余空行和不属于正文的内容
            if content:
                # 去除连续空行，只保留一行
                content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
                
                # 过滤不属于正文的内容
                import re
                # 定义要过滤的内容模式
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
                
                # 应用所有过滤模式
                for pattern in filter_patterns:
                    content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
                
                # 再次清理空行
                content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
                
                paragraph_count = content.count('\n') + 1
                logger.info(f"成功提取36氪正文内容，长度: {len(content)}, 段落数: {paragraph_count}")
            else:
                logger.warning(f"无法提取36氪正文内容: {news_url}")
            
            # 解析阅读量
            read_count = 0
            read_tag = soup.find('span', class_='read-count') or soup.find('span', class_='view-count') or soup.find('div', class_='post-views')
            if read_tag:
                try:
                    read_count = int(read_tag.text.strip().replace('阅读', '').replace('浏览', '').replace('次', ''))
                except:
                    read_count = 0
            
            # 生成source_id（使用url的最后部分）
            source_id = news_url.split('/')[-1] if '/' in news_url else news_url
            if '.' in source_id:
                source_id = source_id.split('.')[0]
            
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
                'is_valid': True,
                'is_ad': False  # 后续通过数据清洗模块识别广告
            }
            
            # 保存到数据库
            self.save_to_database(news_data)
        except Exception as e:
            logger.error(f"爬取新闻详情失败: {e}", exc_info=True)
