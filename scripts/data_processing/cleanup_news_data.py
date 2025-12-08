#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清理和恢复新闻数据的脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from news_analysis.models import News

def cleanup_news_data():
    """清理和恢复新闻数据"""
    print("开始清理新闻数据...")
    
    # 统计当前数据情况
    total_news = News.objects.count()
    valid_news = News.objects.filter(is_valid=True).count()
    invalid_news = News.objects.filter(is_valid=False).count()
    
    print(f"当前数据统计: 总新闻数 {total_news}, 有效新闻 {valid_news}, 无效新闻 {invalid_news}")
    
    # 查看无效新闻的详细情况
    invalid_news_list = News.objects.filter(is_valid=False)
    print(f"\n无效新闻详情:")
    for news in invalid_news_list:
        print(f"ID: {news.id}, 平台: {news.platform}, 标题: '{news.title}', 创建时间: {news.created_at}")
    
    # 删除空标题的无效新闻
    empty_title_news = News.objects.filter(is_valid=False, title='')
    empty_count = empty_title_news.count()
    
    if empty_count > 0:
        print(f"\n删除 {empty_count} 条空标题的无效新闻...")
        empty_title_news.delete()
        print("删除完成！")
    
    # 重新统计数据情况
    total_news = News.objects.count()
    valid_news = News.objects.filter(is_valid=True).count()
    invalid_news = News.objects.filter(is_valid=False).count()
    
    print(f"\n清理后数据统计: 总新闻数 {total_news}, 有效新闻 {valid_news}, 无效新闻 {invalid_news}")
    
    print("\n数据清理完成！")

if __name__ == "__main__":
    cleanup_news_data()
