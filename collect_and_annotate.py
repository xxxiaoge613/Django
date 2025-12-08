#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻样本收集和标注脚本
用于从数据库中导出新闻数据并进行情感标注
"""

import sys
import os
import json
from datetime import datetime

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Django环境初始化
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from news_analysis.models import News

def collect_news_from_db(limit=100):
    """
    从数据库中收集新闻样本
    
    Args:
        limit: 收集的新闻数量上限
        
    Returns:
        list: 新闻样本列表
    """
    print(f"从数据库中收集前{limit}条有效新闻...")
    
    # 查询有效且非广告的新闻
    news_list = News.objects.filter(
        is_valid=True,
        is_ad=False
    ).order_by('-publish_time')[:limit]
    
    news_samples = []
    for news in news_list:
        news_samples.append({
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'publish_time': news.publish_time.strftime('%Y-%m-%d %H:%M:%S') if news.publish_time else None,
            'source': news.source,
            'category': news.category,
            'url': news.url
        })
    
    print(f"成功收集{len(news_samples)}条新闻样本")
    return news_samples

def save_news_samples(news_samples, filename=None):
    """
    保存新闻样本到文件
    
    Args:
        news_samples: 新闻样本列表
        filename: 保存文件名，默认使用当前时间生成
    """
    if not filename:
        filename = f"news_samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(news_samples, f, ensure_ascii=False, indent=2)
    
    print(f"新闻样本已保存到{filename}")
    return filename

def load_news_samples(filename):
    """
    从文件中加载新闻样本
    
    Args:
        filename: 文件名
        
    Returns:
        list: 新闻样本列表
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def annotate_news_samples(news_samples):
    """
    手动标注新闻样本的情感
    
    Args:
        news_samples: 新闻样本列表
        
    Returns:
        list: 标注后的新闻样本列表
    """
    print("\n开始标注新闻样本...")
    print("标注说明：")
    print("  0 - 负面新闻")
    print("  1 - 中性新闻")
    print("  2 - 正面新闻")
    print("  q - 退出标注")
    print("  s - 保存当前进度并退出")
    print("-" * 50)
    
    annotated_samples = []
    
    for i, news in enumerate(news_samples):
        if 'sentiment' in news and news['sentiment'] is not None:
            print(f"样本 {i+1}/{len(news_samples)} 已标注，跳过...")
            annotated_samples.append(news)
            continue
        
        print(f"\n样本 {i+1}/{len(news_samples)}：")
        print(f"ID: {news['id']}")
        print(f"标题: {news['title']}")
        print(f"来源: {news['source']}")
        print(f"发布时间: {news['publish_time']}")
        print(f"分类: {news['category']}")
        print(f"内容: {news['content'][:200]}...")
        
        while True:
            user_input = input("请输入情感标注 (0/1/2/q/s): ").strip()
            
            if user_input == 'q':
                print("退出标注")
                return annotated_samples
            elif user_input == 's':
                print("保存当前进度并退出")
                return annotated_samples
            elif user_input in ['0', '1', '2']:
                sentiment = int(user_input)
                news['sentiment'] = sentiment
                news['annotated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                annotated_samples.append(news)
                
                # 输出标注结果
                sentiment_map = {0: '负面', 1: '中性', 2: '正面'}
                print(f"标注结果：{sentiment_map[sentiment]}")
                break
            else:
                print("输入无效，请重新输入")
    
    return annotated_samples

def generate_test_set(filename='annotated_news_samples.json', test_size=50):
    """
    从标注好的样本中生成测试集
    
    Args:
        filename: 标注好的样本文件名
        test_size: 测试集大小
        
    Returns:
        tuple: (训练集, 测试集)
    """
    # 加载标注好的样本
    annotated_samples = load_news_samples(filename)
    
    # 确保样本已经标注
    annotated_samples = [sample for sample in annotated_samples if 'sentiment' in sample and sample['sentiment'] is not None]
    
    if len(annotated_samples) < test_size:
        print(f"标注样本数量不足，仅有{len(annotated_samples)}条，无法生成{test_size}条的测试集")
        return [], []
    
    # 简单的随机分割（实际应用中应使用更科学的方法）
    import random
    random.seed(42)  # 设置随机种子，确保结果可复现
    random.shuffle(annotated_samples)
    
    test_set = annotated_samples[:test_size]
    train_set = annotated_samples[test_size:]
    
    print(f"生成测试集：{len(test_set)}条样本")
    print(f"剩余训练集：{len(train_set)}条样本")
    
    # 保存测试集
    test_filename = f"test_set_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_news_samples(test_set, test_filename)
    
    # 保存训练集
    train_filename = f"train_set_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_news_samples(train_set, train_filename)
    
    return train_set, test_set

def main():
    """
    主函数
    """
    print("=" * 60)
    print("新闻样本收集和标注工具")
    print("=" * 60)
    
    while True:
        print("\n请选择操作：")
        print("1. 从数据库收集新闻样本")
        print("2. 加载现有样本并标注")
        print("3. 生成测试集")
        print("4. 退出")
        
        choice = input("请输入选项 (1/2/3/4): ").strip()
        
        if choice == '1':
            # 从数据库收集新闻样本
            limit = input("请输入要收集的新闻数量（默认100）: ").strip()
            limit = int(limit) if limit.isdigit() else 100
            news_samples = collect_news_from_db(limit)
            filename = save_news_samples(news_samples)
            print(f"\n下一步建议：使用选项2加载{filename}并进行标注")
            
        elif choice == '2':
            # 加载现有样本并标注
            filename = input("请输入要加载的样本文件名（留空使用最新生成的文件）: ").strip()
            if not filename:
                # 查找最新生成的样本文件
                import glob
                sample_files = glob.glob('news_samples_*.json')
                if sample_files:
                    sample_files.sort(key=os.path.getmtime, reverse=True)
                    filename = sample_files[0]
                    print(f"使用最新生成的样本文件：{filename}")
                else:
                    print("未找到样本文件，请先使用选项1收集样本")
                    continue
            
            if not os.path.exists(filename):
                print(f"文件 {filename} 不存在")
                continue
            
            # 加载样本
            news_samples = load_news_samples(filename)
            
            # 进行标注
            annotated_samples = annotate_news_samples(news_samples)
            
            # 保存标注结果
            annotated_filename = f"annotated_{os.path.basename(filename)}"
            save_news_samples(annotated_samples, annotated_filename)
            print(f"\n标注结果已保存到 {annotated_filename}")
            
        elif choice == '3':
            # 生成测试集
            filename = input("请输入标注好的样本文件名（默认使用最新的annotated文件）: ").strip()
            if not filename:
                # 查找最新的标注文件
                import glob
                annotated_files = glob.glob('annotated_*.json')
                if annotated_files:
                    annotated_files.sort(key=os.path.getmtime, reverse=True)
                    filename = annotated_files[0]
                    print(f"使用最新的标注文件：{filename}")
                else:
                    print("未找到标注文件，请先使用选项2进行标注")
                    continue
            
            if not os.path.exists(filename):
                print(f"文件 {filename} 不存在")
                continue
            
            # 生成测试集
            test_size = input("请输入测试集大小（默认50）: ").strip()
            test_size = int(test_size) if test_size.isdigit() else 50
            generate_test_set(filename, test_size)
            
        elif choice == '4':
            print("退出程序")
            break
        else:
            print("输入无效，请重新输入")

if __name__ == "__main__":
    main()
