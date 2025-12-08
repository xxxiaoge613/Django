import requests
from bs4 import BeautifulSoup

# 获取量子位网站完整HTML
url = 'https://www.qbitai.com/category/%e8%b5%84%e8%ae%af'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)

# 保存完整HTML到文件
with open('quantum_bit_full.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"已保存量子位网站完整HTML到 quantum_bit_full.html")
print(f"状态码: {response.status_code}")
print(f"页面大小: {len(response.text)} 字符")

# 分析HTML结构
soup = BeautifulSoup(response.text, 'html.parser')

# 查找所有可能包含新闻的标签
print("\n=== 查找所有可能包含新闻的标签 ===")

# 查找所有div标签，按class分组
print("\n1. 所有div标签按class分组:")
div_classes = {}
for div in soup.find_all('div'):
    classes = tuple(div.get('class', []))
    if classes:
        div_classes[classes] = div_classes.get(classes, 0) + 1

# 只显示出现次数>1的class
common_divs = {k: v for k, v in div_classes.items() if v > 1}
for i, (classes, count) in enumerate(sorted(common_divs.items(), key=lambda x: x[1], reverse=True)[:20]):
    print(f"  {i+1}. {classes}: {count}次")

# 查找所有a标签，按父元素class分组
print("\n2. 所有a标签按父元素class分组:")
a_parent_classes = {}
for a in soup.find_all('a'):
    if a.text.strip() and len(a.text.strip()) > 5:
        parent = a.parent
        if parent:
            classes = tuple(parent.get('class', []))
            if classes:
                a_parent_classes[classes] = a_parent_classes.get(classes, 0) + 1

# 只显示出现次数>1的父元素class
common_a_parents = {k: v for k, v in a_parent_classes.items() if v > 1}
for i, (classes, count) in enumerate(sorted(common_a_parents.items(), key=lambda x: x[1], reverse=True)[:20]):
    print(f"  {i+1}. {classes}: {count}次")

# 查找所有带有href的a标签，显示实际内容
print("\n3. 查找可能的新闻链接:")
news_links = []
for a in soup.find_all('a'):
    href = a.get('href')
    text = a.text.strip()
    if href and text and len(text) > 5:
        # 排除导航链接
        if not any(keyword in href for keyword in ['#', 'javascript:', 'mailto:', 'tel:']):
            # 排除太短的链接
            if len(href) > 10:
                news_links.append((text, href))

# 显示前20个可能的新闻链接
for i, (text, href) in enumerate(news_links[:20]):
    print(f"  {i+1}. {text[:50]}... -> {href}")