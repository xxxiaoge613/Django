import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from news_analysis.models import News, SentimentAnalysis
from django.db import models

# 调试情感分析查询
print("=== 调试情感分析查询 ===")

# 获取所有已分析的新闻ID
analyzed_news_ids = SentimentAnalysis.objects.values_list('news_id', flat=True)
print(f"已分析的新闻ID: {list(analyzed_news_ids)}")
print(f"已分析的新闻数量: {len(list(analyzed_news_ids))}")

# 获取所有有效新闻
all_valid_news = News.objects.filter(is_valid=True, is_ad=False)
print(f"\n所有有效新闻数量: {all_valid_news.count()}")

# 手动计算未分析的新闻
analyzed_set = set(analyzed_news_ids)
all_news_ids = set(all_valid_news.values_list('id', flat=True))
missing_analysis = all_news_ids - analyzed_set
print(f"\n未分析的新闻ID: {missing_analysis}")
print(f"未分析的新闻数量: {len(missing_analysis)}")

# 尝试不同的查询方式
print("\n=== 尝试不同的查询方式 ===")

# 方式1: 使用exclude和sentiment__isnull
news_list1 = News.objects.filter(is_valid=True, is_ad=False).exclude(sentiment__isnull=False)
print(f"方式1 (exclude sentiment__isnull=False): {news_list1.count()} 条")

# 方式2: 使用sentiment__isnull
news_list2 = News.objects.filter(is_valid=True, is_ad=False, sentiment__isnull=True)
print(f"方式2 (sentiment__isnull=True): {news_list2.count()} 条")

# 方式3: 使用not in
analyzed_news_ids_list = list(analyzed_news_ids)
if analyzed_news_ids_list:
    news_list3 = News.objects.filter(is_valid=True, is_ad=False).exclude(id__in=analyzed_news_ids_list)
else:
    news_list3 = News.objects.filter(is_valid=True, is_ad=False)
print(f"方式3 (exclude id__in): {news_list3.count()} 条")

# 打印一些新闻详情
print("\n=== 新闻详情示例 ===")
sample_news = News.objects.filter(is_valid=True, is_ad=False)[:5]
for news in sample_news:
    has_sentiment = hasattr(news, 'sentiment') and news.sentiment is not None
    print(f"新闻ID: {news.id}, 标题: {news.title[:20]}..., 有情感分析: {has_sentiment}")
    if has_sentiment:
        print(f"  情感类型: {news.sentiment.sentiment_type}, 情感得分: {news.sentiment.sentiment_score}")