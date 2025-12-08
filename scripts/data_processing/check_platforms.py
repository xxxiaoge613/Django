#!/usr/bin/env python
"""检查数据库中的平台信息"""

import os
import sys

# 确保Django设置被正确加载
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.models import News

def main():
    # 查询所有平台
    print("=== 数据库中所有平台信息 ===")
    
    # 查询所有新闻的platform字段
    all_platforms = News.objects.values_list('platform', flat=True)
    print(f"\n所有新闻平台总数: {all_platforms.count()}")
    
    # 查询不同的平台
    distinct_platforms = News.objects.values_list('platform', flat=True).distinct()
    print(f"不同的平台数量: {distinct_platforms.count()}")
    
    # 显示不同的平台
    print("\n不同的平台列表:")
    for platform in distinct_platforms:
        count = News.objects.filter(platform=platform).count()
        print(f"- {platform}: {count} 条新闻")
    
    # 检查是否有空白或无效平台
    print("\n检查空白或无效平台:")
    empty_platforms = News.objects.filter(platform__in=['', None, ' '])
    print(f"空白平台数量: {empty_platforms.count()}")
    
    # 检查平台名称是否有前后空格
    print("\n检查平台名称是否有前后空格:")
    for platform in distinct_platforms:
        if platform.strip() != platform:
            print(f"- '{platform}' 有前后空格")
    
    # 检查平台名称是否有特殊字符
    print("\n检查平台名称的ASCII表示:")
    for platform in distinct_platforms:
        print(f"- '{platform}': {repr(platform)}")

if __name__ == "__main__":
    main()
