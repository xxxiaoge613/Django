#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情感分析模型性能测试脚本
用于评估当前SnowNLP情感分析模型在新闻文本上的性能
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_analysis.sentiment_analysis.analyzer import SentimentAnalyzer

def evaluate_sentiment_model():
    """
    评估情感分析模型的性能
    """
    # 初始化情感分析器
    analyzer = SentimentAnalyzer()
    
    # 标注好的测试样本 - 格式：(文本, 真实情感标签)
    # 真实情感标签：0-负面，1-中性，2-正面
    test_samples = [
        # 负面新闻样本
        ("爱马仕继承人被骗160亿美元，金融诈骗案件细节曝光", 0),
        ("公司业绩大幅下滑，股价暴跌20%", 0),
        ("经济增长放缓，失业率上升", 0),
        ("产品质量问题引发消费者投诉，品牌声誉受损", 0),
        ("企业债务违约，面临破产风险", 0),
        ("市场需求萎缩，公司裁员10%", 0),
        ("投资项目失败，损失惨重", 0),
        ("监管政策收紧，行业前景堪忧", 0),
        ("竞争对手抢占市场份额，公司利润下降", 0),
        ("供应链断裂，生产停滞", 0),
        
        # 中性新闻样本
        ("公司发布年度报告，各项指标符合预期", 1),
        ("行业协会举办年度会议，探讨发展趋势", 1),
        ("新产品上市，市场反应平淡", 1),
        ("公司宣布管理层变动，新任CEO上任", 1),
        ("行业数据显示，市场规模保持稳定", 1),
        ("公司与供应商签订长期合作协议", 1),
        ("技术创新取得突破，专利申请成功", 1),
        ("公司举办投资者关系活动，解答市场疑问", 1),
        ("行业标准更新，企业需调整生产流程", 1),
        ("公司发布社会责任报告，强调可持续发展", 1),
        
        # 正面新闻样本
        ("公司业绩超预期，股价上涨15%", 2),
        ("新产品销量创新高，市场份额提升", 2),
        ("经济增长加速，就业形势好转", 2),
        ("企业获得重要奖项，品牌影响力提升", 2),
        ("投资项目成功，回报率达30%", 2),
        ("市场需求旺盛，公司扩大生产规模", 2),
        ("技术突破带来成本降低，利润空间扩大", 2),
        ("公司成功并购竞争对手，市场地位巩固", 2),
        ("行业政策利好，企业发展迎来机遇", 2),
        ("消费者满意度提升，品牌忠诚度增强", 2),
    ]
    
    # 预测结果
    predictions = []
    true_labels = []
    
    print("开始评估情感分析模型性能...")
    print(f"测试样本数量：{len(test_samples)}")
    print("=" * 60)
    
    for i, (text, true_label) in enumerate(test_samples):
        # 使用当前模型进行预测
        result = analyzer.analyze_sentiment(text)
        pred_label = result['sentiment_type']
        
        # 将预测标签转换为数字：0-负面，1-中性，2-正面
        if pred_label == '负面':
            pred_num = 0
        elif pred_label == '中性':
            pred_num = 1
        else:  # 正面
            pred_num = 2
        
        predictions.append(pred_num)
        true_labels.append(true_label)
        
        # 输出当前样本的分析结果
        print(f"样本 {i+1}: ")
        print(f"  文本：{text}")
        print(f"  真实情感：{true_label} ({'负面' if true_label == 0 else '中性' if true_label == 1 else '正面'})")
        print(f"  预测情感：{pred_num} ({pred_label})")
        print(f"  情感得分：{result['sentiment_score']:.4f}")
        print(f"  SnowNLP得分：{result['snow_score']:.4f}")
        print(f"  自定义词典得分：{result['financial_score']:.4f}")
        print(f"  预测结果：{'正确' if pred_num == true_label else '错误'}")
        print()
    
    # 计算性能指标
    def calculate_metrics(true, pred, num_classes=3):
        """计算多分类模型的性能指标"""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        accuracy = accuracy_score(true, pred)
        precision = precision_score(true, pred, average='weighted')
        recall = recall_score(true, pred, average='weighted')
        f1 = f1_score(true, pred, average='weighted')
        
        # 计算各分类的详细指标
        precision_per_class = precision_score(true, pred, average=None)
        recall_per_class = recall_score(true, pred, average=None)
        f1_per_class = f1_score(true, pred, average=None)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'precision_per_class': precision_per_class,
            'recall_per_class': recall_per_class,
            'f1_per_class': f1_per_class
        }
    
    # 检查是否安装了sklearn
    try:
        metrics = calculate_metrics(true_labels, predictions)
    except ImportError:
        print("未安装scikit-learn，无法计算详细指标")
        return
    
    # 输出性能指标
    print("=" * 60)
    print("性能评估结果：")
    print(f"准确率 (Accuracy): {metrics['accuracy']:.4f}")
    print(f"加权精确率 (Weighted Precision): {metrics['precision']:.4f}")
    print(f"加权召回率 (Weighted Recall): {metrics['recall']:.4f}")
    print(f"加权F1值 (Weighted F1): {metrics['f1']:.4f}")
    print()
    print("各类别详细指标：")
    print(f"负面新闻 - 精确率: {metrics['precision_per_class'][0]:.4f}, 召回率: {metrics['recall_per_class'][0]:.4f}, F1值: {metrics['f1_per_class'][0]:.4f}")
    print(f"中性新闻 - 精确率: {metrics['precision_per_class'][1]:.4f}, 召回率: {metrics['recall_per_class'][1]:.4f}, F1值: {metrics['f1_per_class'][1]:.4f}")
    print(f"正面新闻 - 精确率: {metrics['precision_per_class'][2]:.4f}, 召回率: {metrics['recall_per_class'][2]:.4f}, F1值: {metrics['f1_per_class'][2]:.4f}")
    print("=" * 60)
    
    # 统计混淆矩阵
    def confusion_matrix(true, pred, num_classes=3):
        """生成混淆矩阵"""
        cm = [[0 for _ in range(num_classes)] for _ in range(num_classes)]
        for t, p in zip(true, pred):
            cm[t][p] += 1
        return cm
    
    cm = confusion_matrix(true_labels, predictions)
    
    print("混淆矩阵：")
    print("真实标签\\预测标签 | 负面(0) | 中性(1) | 正面(2)")
    print("-" * 50)
    labels = ["负面(0)", "中性(1)", "正面(2)"]
    for i in range(3):
        row = labels[i] + " |"
        for j in range(3):
            row += f" {cm[i][j]:^8} |"
        print(row)
    print("-" * 50)
    
    # 分析错误样本
    print("\n错误分析：")
    error_count = 0
    for i, (text, true_label) in enumerate(test_samples):
        pred_num = predictions[i]
        if pred_num != true_label:
            error_count += 1
            true_sent = '负面' if true_label == 0 else '中性' if true_label == 1 else '正面'
            pred_sent = '负面' if pred_num == 0 else '中性' if pred_num == 1 else '正面'
            result = analyzer.analyze_sentiment(text)
            print(f"错误样本 {error_count}:")
            print(f"  文本：{text}")
            print(f"  真实情感：{true_sent}")
            print(f"  预测情感：{pred_sent}")
            print(f"  情感得分：{result['sentiment_score']:.4f}")
            print()
    
    print(f"\n总错误样本数：{error_count}/{len(test_samples)}")
    print(f"错误率：{error_count/len(test_samples):.2%}")

if __name__ == "__main__":
    evaluate_sentiment_model()
