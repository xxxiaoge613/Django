#!/usr/bin/env python
"""检查数据库中的新闻数据"""

import os
import sys

# 确保Django设置被正确加载
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.models import News

def main():
    # 统计总新闻数
    total_news = News.objects.count()
    print(f"数据库中共有 {total_news} 条新闻")
    
    # 按平台统计
    platforms = News.objects.values_list('platform', flat=True).distinct()
    for platform in platforms:
        count = News.objects.filter(platform=platform).count()
        print(f"  {platform}: {count} 条")
    
    # 显示最近5条新闻（按ID排序）
    print("\n最近5条新闻：")
    recent_news = News.objects.order_by('-id')[:5]
    for news in recent_news:
        title = news.title[:50] + "..." if len(news.title) > 50 else news.title
        print(f"  标题：{title}")
        print(f"  平台：{news.platform}")
        print(f"  时间：{news.publish_time}")
        print(f"  URL：{news.url}")
        print(f"  内容长度：{len(news.content)} 字符")
        print()

if __name__ == "__main__":
    main()
