#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试正面新闻阈值优化效果
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def test_positive_threshold_optimization():
    """测试不同正面阈值下的正面新闻识别效果"""
    print("=== 测试不同正面阈值下的正面新闻识别效果 ===")
    
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 测试样本，包含明显的正面新闻
    test_samples = [
        "公司业绩超预期，股价上涨15%",
        "新产品销量创新高，市场份额提升",
        "经济增长加速，就业形势好转",
        "企业获得重要奖项，品牌影响力提升",
        "投资项目成功，回报率达30%",
        "市场需求旺盛，公司扩大生产规模",
        "技术突破带来成本降低，利润空间扩大",
        "公司成功并购竞争对手，市场地位巩固",
        "行业政策利好，企业发展迎来机遇",
        "消费者满意度提升，品牌忠诚度增强",
        "融资数亿、营收过亿！黄仁勋频频关注的具身赛道隐形冠军浮出水面",
        "腾讯Q3财报：AI生态价值释放，To B营收双位数增长至582亿元",
        "百度文库网盘发布GenFlow3.0，活跃用户超2000万",
        "openEuler发布超节点操作系统，引领AI时代",
        "AI视频进入‘加速度’时代：30%加速＋细节随手P",
        "微博7800美元训的大模型，数学能力超了DeepSeek-R1",
        "教育行业首个AI Agent落地！斑马口语‘超人类外教’诞生"
    ]
    
    print(f"\n测试样本数量: {len(test_samples)}")
    
    # 测试不同的正面阈值
    thresholds = [0.53, 0.52, 0.51, 0.50]
    
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
        print(f"\n=== 测试正面阈值: {threshold} ===")
        
        # 统计结果
        positive_count = 0
        neutral_count = 0
        negative_count = 0
        
        for sample in sample_results:
            text = sample['text']
            score = sample['score']
            
            # 根据当前阈值确定情感类型
            if score > threshold:
                sentiment_type = '正面'
            elif score < 0.50:
                sentiment_type = '负面'
            else:
                sentiment_type = '中性'
            
            print(f"文本: {text}")
            print(f"得分: {score:.4f}")
            print(f"类型: {sentiment_type}")
            print("-" * 50)
            
            if sentiment_type == '正面':
                positive_count += 1
            elif sentiment_type == '负面':
                negative_count += 1
            else:
                neutral_count += 1
        
        print(f"\n阈值 {threshold} 下的结果:")
        print(f"正面新闻: {positive_count}")
        print(f"中性新闻: {neutral_count}")
        print(f"负面新闻: {negative_count}")

if __name__ == "__main__":
    test_positive_threshold_optimization()
