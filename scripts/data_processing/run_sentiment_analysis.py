import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

# 运行情感分析
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_from_database()
    print(f"情感分析完成: 共分析 {result['analyzed_count']} 条新闻")
    print(f"正面: {result['positive_count']}, 负面: {result['negative_count']}, 中性: {result['neutral_count']}")