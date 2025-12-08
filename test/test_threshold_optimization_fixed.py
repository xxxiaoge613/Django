#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试阈值优化效果（修复了递归错误）
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def test_threshold_optimization():
    """测试不同阈值下的负面新闻识别效果"""
    print("=== 测试不同阈值下的负面新闻识别效果 ===")
    
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 测试样本，包含明显的负面新闻
    test_samples = [
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
        "核心技术人员离职，研发项目受挫",
        "甜蜜生意萎缩，糖果正被谁抛弃？",
        "华为云大调整，读懂三个核心问题",
        "马斯克开始用Grok替代员工了！最惨部门裁员90%"
    ]
    
    print(f"\n测试样本数量: {len(test_samples)}")
    
    # 测试不同的负面阈值
    thresholds = [0.47, 0.48, 0.49, 0.50]
    
    # 先获取所有样本的原始情感得分
    sample_results = []
    for text in test_samples:
        result = analyzer.analyze_sentiment(text)
        sample_results.append({
            'text': text,
            'score': result['sentiment_score'],
            'original_type': result['sentiment_type']
        })
    
    # 测试不同阈值
    for threshold in thresholds:
        print(f"\n=== 测试负面阈值: {threshold} ===")
        
        # 统计结果
        negative_count = 0
        neutral_count = 0
        positive_count = 0
        
        for sample in sample_results:
            text = sample['text']
            score = sample['score']
            
            # 根据当前阈值确定情感类型
            if score > 0.53:
                sentiment_type = '正面'
            elif score < threshold:
                sentiment_type = '负面'
            else:
                sentiment_type = '中性'
            
            print(f"文本: {text}")
            print(f"得分: {score:.4f}")
            print(f"类型: {sentiment_type}")
            print("-" * 50)
            
            if sentiment_type == '负面':
                negative_count += 1
            elif sentiment_type == '正面':
                positive_count += 1
            else:
                neutral_count += 1
        
        print(f"\n阈值 {threshold} 下的结果:")
        print(f"负面新闻: {negative_count}")
        print(f"中性新闻: {neutral_count}")
        print(f"正面新闻: {positive_count}")

if __name__ == "__main__":
    test_threshold_optimization()
