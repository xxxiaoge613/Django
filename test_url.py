from django.test import Client
import sys

# 创建测试客户端
client = Client()

# 测试修复后的URL
response = client.get('/comment/9/like/')

# 打印响应状态码
print(f"响应状态码: {response.status_code}")
print(f"响应内容: {response.content}")

# 退出程序
sys.exit(0 if response.status_code == 200 or response.status_code == 302 else 1)