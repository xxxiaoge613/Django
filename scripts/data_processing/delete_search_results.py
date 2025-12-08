#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除数据库中所有搜索结果页面的数据
"""

import os
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.models import News

def delete_search_results():
    """删除所有URL包含/search的搜索结果页面"""
    print("开始删除搜索结果页面数据...")
    
    # 查询所有URL包含/search的新闻
    search_results = News.objects.filter(url__icontains='/search')
    total_count = search_results.count()
    
    if total_count == 0:
        print("没有找到搜索结果页面数据")
        return
    
    print(f"找到 {total_count} 条搜索结果页面数据")
    
    # 输出前5条数据的信息，供确认
    print("\n前5条搜索结果页面数据：")
    for news in search_results[:5]:
        print(f"- 标题: {news.title}")
        print(f"  URL: {news.url}")
        print(f"  平台: {news.platform}")
        print(f"  状态: {'有效' if news.is_valid else '无效'}")
        print()
    
    # 确认删除
    confirm = input(f"确认删除这 {total_count} 条搜索结果页面数据吗？(y/n): ")
    if confirm.lower() != 'y':
        print("取消删除操作")
        return
    
    # 执行删除操作
    deleted_count, _ = search_results.delete()
    
    print(f"\n删除完成！共删除 {deleted_count} 条搜索结果页面数据")

if __name__ == "__main__":
    delete_search_results()