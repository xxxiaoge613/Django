#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试量子位爬虫的脚本
"""

import requests
from bs4 import BeautifulSoup
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_quantum_spider():
    """调试量子位爬虫"""
    base_url = 'https://www.qbitai.com'
    category_url = f'{base_url}/category/%e8%b5%84%e8%ae%af/page/1'
    
    logger.info(f"正在请求页面: {category_url}")
    
    # 发送请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(category_url, headers=headers)
    response.raise_for_status()
    
    logger.info(f"页面请求成功，状态码: {response.status_code}")
    
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 保存页面内容到文件，方便查看
    with open('quantum_bit_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    logger.info("页面内容已保存到 quantum_bit_page.html")
    
    # 查找新闻列表项
    logger.info("开始查找新闻列表项...")
    
    # 尝试多种选择器
    selectors = [
        '.picture_text',
        '.article-item',
        '.post-item',
        '.news-item',
        '.entry',
        '.post'
    ]
    
    for selector in selectors:
        news_items = soup.select(selector)
        logger.info(f"使用选择器 '{selector}' 找到 {len(news_items)} 条新闻")
        
        if news_items:
            logger.info(f"第1条新闻的HTML结构:")
            logger.info(news_items[0].prettify())
            break
    
    # 查看页面中的所有h4标签
    logger.info("\n页面中的所有h4标签:")
    h4_tags = soup.find_all('h4')
    for h4 in h4_tags[:5]:
        logger.info(f"h4标签内容: {h4.text.strip()}")
        logger.info(f"h4标签HTML: {h4.prettify()}")
    
    # 查看页面中的所有a标签
    logger.info("\n页面中包含文本的a标签:")
    a_tags = soup.find_all('a')
    text_a_tags = [a for a in a_tags if a.text.strip() and len(a.text.strip()) > 10]
    for a in text_a_tags[:5]:
        logger.info(f"a标签文本: {a.text.strip()}")
        logger.info(f"a标签href: {a.get('href', '')}")

if __name__ == "__main__":
    debug_quantum_spider()
