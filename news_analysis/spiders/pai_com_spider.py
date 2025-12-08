import logging
import os
import django
from django.conf import settings
# 确保Django环境已初始化
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
    django.setup()

from playwright.sync_api import sync_playwright
from abc import ABC, abstractmethod
from datetime import datetime
from django.utils.timezone import make_aware
from .base_spider import BaseSpider

logger = logging.getLogger(__name__)

class PaiComSpider(BaseSpider):
    """电商派爬虫，使用playwright进行动态网页爬取"""
    
    def __init__(self):
        super().__init__(platform_name='电商派')
        self.base_url = 'https://www.pai.com.cn'
        self.playwright = None
        self.browser = None
        self.page = None
    
    def __enter__(self):
        """上下文管理器入口，初始化playwright"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
                headless=True,  # 启用无头模式
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
        self.page = self.browser.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，关闭资源"""
        self.close()
    
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
    
    def crawl_news_list(self, page=1):
        """爬取电商派新闻列表"""
        try:
            self._ensure_playwright_initialized()
            url = self.base_url
            logger.info(f"开始爬取电商派新闻列表")
            
            # 使用playwright访问页面
            self.page.goto(url, wait_until='networkidle', timeout=60000)
            
            # 等待页面加载完成
            self.page.wait_for_selector('main', timeout=30000)
            
            # 使用用户提供的精确新闻列表容器选择器
            news_container = self.page.locator('body > div.relative.flex.min-h-screen.flex-col > main > div > div.flex-1 > div:nth-child(4) > div:nth-child(2) > div.block')
            
            # 爬取所有找到的新闻，不限制数量
            item_count = self.page.locator('body > div.relative.flex.min-h-screen.flex-col > main > div > div.flex-1 > div:nth-child(4) > div:nth-child(2) > div.block > div').count()
            logger.info(f"开始爬取所有 {item_count} 条新闻")
            
            # 直接使用索引定位每条新闻，避免使用all()方法
            for i in range(1, item_count + 1):
                try:
                    # 使用用户提供的精确选择器定位单条新闻
                    logger.info(f"开始解析第 {i} 条新闻")
                    
                    # 构建精确的选择器，使用:nth-child()来定位具体新闻
                    base_selector = f'body > div.relative.flex.min-h-screen.flex-col > main > div > div.flex-1 > div:nth-child(4) > div:nth-child(2) > div.block > div:nth-child({i})'
                    
                    # 定位标题和链接
                    title_selector = f'{base_selector} > div.flex.flex-1.flex-col.justify-between > div:nth-child(1) > h3 > a'
                    title_tag = self.page.locator(title_selector)
                    title = title_tag.inner_text().strip()
                    link = title_tag.get_attribute('href')
                    
                    # 处理相对链接
                    if link and link.startswith('/'):
                        news_url = f"{self.base_url}{link}"
                    else:
                        news_url = link or ''
                    
                    if not title or not news_url:
                        logger.warning(f"第 {i} 条新闻缺少标题或链接")
                        continue
                    
                    # 定位作者
                    author_selector = f'{base_selector} > div.flex.flex-1.flex-col.justify-between > div.mt-1.flex.items-center.text-sm > div:nth-child(2)'
                    author_tag = self.page.locator(author_selector)
                    author = author_tag.inner_text().strip()
                    
                    # 定位发布时间
                    time_selector = f'{base_selector} > div.flex.flex-1.flex-col.justify-between > div.mt-1.flex.items-center.text-sm > div.ml-3.text-muted-foreground'
                    time_tag = self.page.locator(time_selector)
                    time_text = time_tag.inner_text().strip()
                    publish_time = self.parse_datetime(time_text)
                    
                    logger.info(f"找到新闻: {title} - {author} - {time_text}")
                    
                    # 爬取新闻详情
                    self.crawl_news_detail(news_url, {
                        'title': title,
                        'author': author,
                        'publish_time': publish_time
                    })
                    
                    # 爬取完详情页后，返回新闻列表页
                    logger.info("返回新闻列表页")
                    self.page.goto(self.base_url, wait_until='networkidle', timeout=30000)
                    
                    # 增加延迟，避免请求过于频繁
                    import time
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"解析第 {i} 条新闻列表项失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"爬取电商派新闻列表失败: {e}")
    
    def crawl_news_detail(self, news_url, basic_info):
        """爬取电商派新闻详情"""
        try:
            self._ensure_playwright_initialized()
            logger.info(f"开始爬取新闻详情: {news_url}")
            
            # 使用playwright访问详情页
            self.page.goto(news_url, wait_until='networkidle')
            
            # 详情页额外增加3-5秒随机等待时间
            import random
            wait_time = random.uniform(3000, 5000)  # 毫秒
            logger.info(f"详情页额外等待: {wait_time/1000:.1f}秒")
            self.page.wait_for_timeout(wait_time)
            
            # 等待内容加载
            self.page.wait_for_selector('main')
            
            # 提取正文内容
            content = ''
            
            # 尝试多种可能的正文选择器，优先使用#post-body
            content_selectors = [
                '#post-body',
                '.article-content',
                '.content',
                '.post-content',
                '.articleDetail-content',
                '.main-content',
                'article',
                'main'
            ]
            
            for selector in content_selectors:
                content_element = self.page.locator(selector)
                if content_element.count() > 0:
                    # 提取所有段落文本
                    paragraphs = content_element.locator('p')
                    if paragraphs.count() > 0:
                        content = '\n'.join([paragraphs.nth(i).inner_text().strip() for i in range(paragraphs.count())])
                        break
                    else:
                        # 如果没有段落，提取整个元素文本
                        content = content_element.inner_text().strip()
                        break
            
            # 清理内容，去除无效信息
            if content:
                # 去除连续空行
                content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
                logger.info(f"成功提取正文内容，长度: {len(content)}")
            else:
                logger.warning(f"无法提取正文内容: {news_url}")
            
            # 解析阅读量
            read_count = 0
            # 电商派可能没有直接显示阅读量，这里暂时设为0
            
            # 生成source_id
            source_id = news_url.split('/')[-1] if '/' in news_url else news_url
            
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
                'is_ad': False
            }
            
            # 保存到数据库
            self.save_to_database(news_data)
            
        except Exception as e:
            logger.error(f"爬取新闻详情失败: {e}")
