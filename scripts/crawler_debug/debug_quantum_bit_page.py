import requests
from bs4 import BeautifulSoup

# 测试量子位新闻页面结构
url = 'https://www.qbitai.com/2025/12/357854.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

# 获取新闻列表页
list_url = 'https://www.qbitai.com/category/%e8%b5%84%e8%ae%af/page/1'
list_response = requests.get(list_url, headers=headers)
list_soup = BeautifulSoup(list_response.text, 'html.parser')

print("=== 量子位新闻列表页分析 ===")

# 查找picture_text类的div
picture_text_divs = list_soup.find_all('div', class_='picture_text')
print(f"\n找到 {len(picture_text_divs)} 个picture_text div")

# 详细分析第一个div
if picture_text_divs:
    first_div = picture_text_divs[0]
    print("\n第一个picture_text div的完整HTML:")
    print(first_div.prettify())
    
    # 查找所有a标签
    a_tags = first_div.find_all('a')
    print(f"\n该div中的a标签数量: {len(a_tags)}")
    for i, a in enumerate(a_tags):
        print(f"\na标签 {i+1}:")
        print(f"  文本: '{a.text.strip()}'")
        print(f"  href: {a.get('href')}")
        print(f"  父元素: {a.parent.name}.{a.parent.get('class', [])}")

print("\n\n=== 量子位新闻详情页分析 ===")

# 获取新闻详情页
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"\n页面标题: {soup.title.text if soup.title else 'None'}")

# 查找新闻标题
print("\n查找新闻标题:")
h1_tags = soup.find_all('h1')
for i, h1 in enumerate(h1_tags):
    print(f"h1[{i}]: '{h1.text.strip()}'")
    print(f"  父元素: {h1.parent.name}.{h1.parent.get('class', [])}")

# 查找内容区域
print("\n查找内容区域:")
content_divs = [
    soup.find('div', class_='article-content'),
    soup.find('div', class_='entry-content'),
    soup.find('div', class_='content'),
    soup.find('article')
]

for i, div in enumerate(content_divs):
    if div:
        print(f"div[{i}] 类名: {div.get('class', [])}")
        print(f"  内容前200字符: '{div.text.strip()[:200]}...'")
        break

# 查找所有可能的内容div
print("\n查找所有可能的内容div:")
all_divs = soup.find_all('div')
for div in all_divs[:50]:  # 只检查前50个
    classes = div.get('class', [])
    if classes and 'content' in str(classes).lower() or 'article' in str(classes).lower() or 'entry' in str(classes).lower():
        print(f"div 类名: {classes}")
        print(f"  内容前100字符: '{div.text.strip()[:100]}...'")
