#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
负面新闻情感分析测试脚本
用于验证模型在识别负面新闻方面的表现
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def test_negative_news():
    """测试模型对负面新闻的识别能力"""
    print("=== 负面新闻情感分析测试 ===")
    
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 负面新闻测试样本
    negative_news_samples = [
        "爱马仕继承人被骗160亿美元，金融诈骗案件细节曝光",
        "公司业绩大幅下滑，股价暴跌20%",
        "经济增长放缓，失业率上升",
        "市场需求萎缩，公司裁员10%",
        "竞争对手抢占市场份额，公司利润下降",
        "产品质量问题引发消费者投诉，品牌声誉受损",
        "企业债务违约，面临破产风险",
        "投资项目失败，损失惨重",
        "监管政策收紧，行业前景堪忧",
        "供应链断裂，生产停滞",
        "股市崩盘，投资者损失惨重",
        "公司财务造假，高管被调查",
        "产品召回事件持续发酵，股价大跌",
        "原材料价格大幅上涨，企业成本压力骤增",
        "核心技术人员离职，研发项目受挫"
    ]
    
    print(f"测试样本数量: {len(negative_news_samples)}")
    print("=" * 50)
    
    # 统计结果
    correct_count = 0
    total_count = len(negative_news_samples)
    
    for i, text in enumerate(negative_news_samples, 1):
        result = analyzer.analyze_sentiment(text)
        sentiment_score = result['sentiment_score']
        sentiment_type = result['sentiment_type']
        snow_score = result['snow_score']
        financial_score = result['financial_score']
        
        # 检查是否正确识别为负面
        is_correct = sentiment_type == '负面'
        if is_correct:
            correct_count += 1
        
        print(f"样本 {i}:")
        print(f"  文本: {text}")
        print(f"  情感得分: {sentiment_score:.4f}")
        print(f"  情感类型: {sentiment_type} {'✓' if is_correct else '✗'}")
        print(f"  SnowNLP得分: {snow_score:.4f}")
        print(f"  自定义词典得分: {financial_score:.4f}")
        print("-" * 50)
    
    # 计算准确率
    accuracy = correct_count / total_count
    print(f"\n=== 测试结果 ===")
    print(f"负面新闻识别准确率: {accuracy:.2%} ({correct_count}/{total_count})")
    
    return accuracy

if __name__ == "__main__":
    test_negative_news()
