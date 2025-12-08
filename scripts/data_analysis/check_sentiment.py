import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from news_analysis.models import News, SentimentAnalysis
from django.db import models

# 检查新闻和情感分析数据的状态
print("=== 新闻数据状态 ===")
total_news = News.objects.count()
valid_news = News.objects.filter(is_valid=True).count()
ad_news = News.objects.filter(is_ad=True).count()

print(f"总新闻数: {total_news}")
print(f"有效新闻数: {valid_news}")
print(f"广告新闻数: {ad_news}")

print("\n=== 情感分析数据状态 ===")
total_analyzed = SentimentAnalysis.objects.count()

# 检查有多少新闻没有情感分析
news_ids = News.objects.values_list('id', flat=True)
sentiment_news_ids = SentimentAnalysis.objects.values_list('news_id', flat=True)
missing_analysis = len(set(news_ids) - set(sentiment_news_ids))

print(f"已分析情感的新闻数: {total_analyzed}")
print(f"未分析情感的新闻数: {missing_analysis}")

# 检查情感分布
print("\n=== 当前情感分布 ===")
sentiment_counts = SentimentAnalysis.objects.values('sentiment_type').annotate(count=models.Count('id'))
for item in sentiment_counts:
    print(f"{item['sentiment_type']}: {item['count']}")