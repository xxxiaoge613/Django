#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热门关键词分析报告生成脚本
从所有新闻详情页的关键词数据中提取并分析热门关键词
"""

import logging
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from collections import Counter
from news_analysis.models import Keyword, News
from news_analysis.views.visualization_views import get_hot_keywords

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def generate_hot_keywords_report():
    """生成热门关键词分析报告"""
    logger.info("开始生成热门关键词分析报告...")
    
    # 1. 收集所有新闻详情页中出现的关键词
    logger.info("\n1. 收集所有新闻的关键词...")
    
    # 获取所有有效新闻
    valid_news = News.objects.filter(is_valid=True, is_ad=False)
    total_news = valid_news.count()
    logger.info(f"共有 {total_news} 篇有效新闻")
    
    # 检查哪些新闻还没有提取关键词
    news_without_keywords = []
    all_keywords = []
    
    for news in valid_news:
        news_keywords = list(Keyword.objects.filter(news=news).values_list('keyword', flat=True))
        if not news_keywords:
            news_without_keywords.append(news)
        else:
            all_keywords.extend(news_keywords)
    
    logger.info(f"已提取关键词的新闻: {total_news - len(news_without_keywords)} 篇")
    logger.info(f"未提取关键词的新闻: {len(news_without_keywords)} 篇")
    
    if news_without_keywords:
        logger.info("建议对未提取关键词的新闻重新提取关键词")
    
    logger.info(f"共收集到 {len(all_keywords)} 个关键词实例")
    
    # 2. 统计各关键词的出现频率
    logger.info("\n2. 统计关键词出现频率...")
    keyword_counter = Counter(all_keywords)
    logger.info(f"共提取到 {len(keyword_counter)} 个不同的关键词")
    
    # 3. 根据频率排序确定热门程度
    logger.info("\n3. 根据频率排序确定热门关键词...")
    sorted_keywords = keyword_counter.most_common()
    
    # 4. 设定合理的热门阈值或数量标准
    logger.info("\n4. 设定热门关键词标准...")
    
    # 设定多种热门关键词选择标准
    hot_keywords_by_count = []
    hot_keywords_by_percentage = []
    
    # 标准1: 取出现频率前20的关键词
    hot_keywords_by_count = sorted_keywords[:20]
    
    # 标准2: 取出现频率超过总新闻数10%的关键词
    threshold_percentage = 0.10
    threshold_count = total_news * threshold_percentage
    
    for keyword, count in sorted_keywords:
        if count >= threshold_count:
            hot_keywords_by_percentage.append((keyword, count))
        else:
            break
    
    logger.info(f"标准1 - 前20个热门关键词: {len(hot_keywords_by_count)} 个")
    logger.info(f"标准2 - 出现频率超过10%的关键词: {len(hot_keywords_by_percentage)} 个 (阈值: {threshold_count:.1f}次)")
    
    # 5. 生成包含热门关键词及其对应出现次数的分析报告
    logger.info("\n5. 生成热门关键词分析报告...")
    
    report_content = "# 热门关键词分析报告\n\n"
    report_content += f"## 报告生成时间\n{django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    report_content += f"## 数据分析基础\n"
    report_content += f"- 有效新闻总数: {total_news} 篇\n"
    report_content += f"- 已提取关键词的新闻: {total_news - len(news_without_keywords)} 篇\n"
    report_content += f"- 关键词实例总数: {len(all_keywords)} 个\n"
    report_content += f"- 不同关键词数量: {len(keyword_counter)} 个\n\n"
    
    report_content += "## 热门关键词结果\n\n"
    
    # 按出现频率排序的热门关键词
    report_content += "### 1. 按出现频率排序的前20个热门关键词\n"
    report_content += "| 排名 | 关键词 | 出现次数 | 覆盖新闻比例 |\n"
    report_content += "|------|--------|----------|--------------|\n"
    
    for rank, (keyword, count) in enumerate(hot_keywords_by_count, 1):
        percentage = (count / total_news) * 100
        report_content += f"| {rank} | {keyword} | {count} | {percentage:.1f}% |\n"
    
    report_content += "\n"
    
    # 按出现频率超过阈值的热门关键词
    if hot_keywords_by_percentage:
        report_content += f"### 2. 出现频率超过{threshold_percentage*100}%的热门关键词\n"
        report_content += "| 关键词 | 出现次数 | 覆盖新闻比例 |\n"
        report_content += "|--------|----------|--------------|\n"
        
        for keyword, count in hot_keywords_by_percentage:
            percentage = (count / total_news) * 100
            report_content += f"| {keyword} | {count} | {percentage:.1f}% |\n"
    
    # 与现有get_hot_keywords函数的结果对比
    report_content += "\n### 3. 与现有热门关键词函数结果对比\n"
    existing_hot_keywords = get_hot_keywords(limit=20)
    report_content += "| 排名 | 现有函数关键词 | 现有函数频率 | 本报告关键词 | 本报告频率 |\n"
    report_content += "|------|----------------|--------------|--------------|------------|\n"
    
    for i in range(20):
        if i < len(existing_hot_keywords) and i < len(hot_keywords_by_count):
            existing = existing_hot_keywords[i]
            current = hot_keywords_by_count[i]
            report_content += f"| {i+1} | {existing['keyword']} | {existing['count']} | {current[0]} | {current[1]} |\n"
        elif i < len(existing_hot_keywords):
            existing = existing_hot_keywords[i]
            report_content += f"| {i+1} | {existing['keyword']} | {existing['count']} | - | - |\n"
        elif i < len(hot_keywords_by_count):
            current = hot_keywords_by_count[i]
            report_content += f"| {i+1} | - | - | {current[0]} | {current[1]} |\n"
    
    # 保存报告到文件
    report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hot_keywords_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logger.info(f"\n5. 报告已生成: {report_file}")
    
    # 打印报告摘要
    logger.info("\n6. 报告摘要:")
    logger.info("\n### 热门关键词Top 10")
    for i, (keyword, count) in enumerate(sorted_keywords[:10], 1):
        logger.info(f"{i}. {keyword}: {count}次")
    
    logger.info(f"\n✅ 热门关键词分析报告生成完成！")
    return report_content

if __name__ == "__main__":
    generate_hot_keywords_report()