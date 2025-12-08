#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复量子位空标题新闻的脚本
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

def fix_empty_titles():
    """修复空标题的量子位新闻"""
    print("开始修复空标题新闻...")
    
    # 查找所有平台为空标题的新闻
    empty_news = News.objects.filter(title='')
    count = empty_news.count()
    
    print(f"找到 {count} 条空标题新闻")
    
    # 将这些新闻标记为无效
    for news in empty_news:
        news.is_valid = False
        news.save()
        print(f"已修复 ID: {news.id}，平台: {news.platform}")
    
    print("修复完成！")

if __name__ == "__main__":
    fix_empty_titles()
