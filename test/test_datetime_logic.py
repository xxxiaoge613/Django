#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试日期时间解析逻辑
"""

from datetime import datetime, timedelta
from django.utils.timezone import make_aware
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_datetime(date_str):
    """解析日期字符串为datetime对象，支持相对时间格式"""
    if not date_str:
        return make_aware(datetime.now())
    
    try:
        now = datetime.now()
        date_str = date_str.strip()
        
        # 处理特殊相对时间格式："昨天"、"前天"
        if '昨天' in date_str:
            # 提取时间部分，例如 "昨天 11:53" -> "11:53"
            time_part = date_str.replace('昨天', '').strip()
            yesterday = now - timedelta(days=1)
            if time_part:
                # 组合日期和时间
                dt_str = f"{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d} {time_part}"
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            else:
                dt = yesterday
            return make_aware(dt)
        elif '前天' in date_str:
            # 提取时间部分，例如 "前天 22:14" -> "22:14"
            time_part = date_str.replace('前天', '').strip()
            day_before_yesterday = now - timedelta(days=2)
            if time_part:
                # 组合日期和时间
                dt_str = f"{day_before_yesterday.year}-{day_before_yesterday.month:02d}-{day_before_yesterday.day:02d} {time_part}"
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            else:
                dt = day_before_yesterday
            return make_aware(dt)
        
        # 处理相对时间格式，如 "11分钟前"、"2小时前"、"3天前"
        relative_time_pattern = re.compile(r'(\d+)(分钟|小时|天)前')
        match = relative_time_pattern.match(date_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit == '分钟':
                dt = now - timedelta(minutes=amount)
            elif unit == '小时':
                dt = now - timedelta(hours=amount)
            elif unit == '天':
                dt = now - timedelta(days=amount)
            else:
                dt = now
                
            return make_aware(dt)
        
        # 尝试多种绝对日期格式
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%m-%d %H:%M',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y'
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # 如果年份不完整，添加当前年份
                if dt.year == 1900:
                    dt = dt.replace(year=now.year)
                return make_aware(dt)
            except ValueError:
                continue
        
        logger.warning(f"无法解析日期格式: {date_str}")
        return make_aware(now)
    except Exception as e:
        logger.error(f"解析日期失败: {e}")
        return make_aware(datetime.now())

def test_datetime_parse():
    """测试日期时间解析功能"""
    logger.info("开始测试日期时间解析功能...")
    
    # 测试用例
    test_cases = [
        "昨天 11:53",
        "前天 22:14",
        "前天 22:03",
        "昨天 11:48",
        "昨天 11:46",
        "昨天 11:42",
        "昨天 09:08",
        "3天前",
        "2小时前",
        "45分钟前",
        "2025-12-03",
        "2025-12-03 12:00",
        "",
        None
    ]
    
    for test_case in test_cases:
        try:
            result = parse_datetime(test_case)
            logger.info(f"输入: '{test_case}' -> 输出: {result}")
        except Exception as e:
            logger.error(f"测试用例 '{test_case}' 失败: {e}")
    
    logger.info("日期时间解析测试完成！")

if __name__ == "__main__":
    test_datetime_parse()
