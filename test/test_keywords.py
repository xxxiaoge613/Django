import os
import sys

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
import django
django.setup()

# 导入测试函数
from news_analysis.views.visualization_views import get_hot_keywords

# 测试获取关键词
print("测试获取热门关键词...")
keywords = get_hot_keywords(limit=20)

print(f"获取到 {len(keywords)} 个关键词:")
for keyword in keywords:
    print(f"  - {keyword['keyword']}: {keyword['count']}")

if not keywords:
    print("警告：未获取到关键词数据！")
