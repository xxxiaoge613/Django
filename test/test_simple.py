#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试：验证情感分析模型的基本功能
"""

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def test_simple():
    """
    简单测试情感分析模型
    """
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 准备简单测试样本
    test_samples = [
        "公司业绩大幅下滑，股价暴跌20%",
        "经济增长加速，就业形势好转",
        "行业协会举办年度会议"
    ]
    
    print("简单测试：情感分析模型")
    print("=" * 50)
    
    # 测试情感分析模型
    for i, text in enumerate(test_samples, 1):
        print(f"样本 {i}:")
        print(f"文本: {text}")
        
        # 进行情感分析
        try:
            sentiment_result = analyzer.analyze_sentiment(text)
            print(f"情感得分: {sentiment_result['sentiment_score']:.4f}")
            print(f"情感类型: {sentiment_result['sentiment_type']}")
            print(f"SnowNLP得分: {sentiment_result['snow_score']:.4f}")
            print(f"自定义词典得分: {sentiment_result['financial_score']:.4f}")
        except Exception as e:
            print(f"分析失败: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_simple()
