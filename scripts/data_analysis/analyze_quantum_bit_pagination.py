import requests
from bs4 import BeautifulSoup

# 发送请求获取页面内容
url = 'https://www.qbitai.com/category/%e8%b5%84%e8%ae%af?page=1'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("=== 页面结构分析 ===")
    
    # 查找新闻列表项
    print("\n1. 新闻列表项：")
    news_selectors = [
        'div.picture_text',
        'article.post',
        'div.article-item',
        'div.post-item',
        'div.main-container div.picture_text',
        'div#primary div.picture_text',
        'div.content-wrapper div.picture_text'
    ]
    
    for selector in news_selectors:
        found = soup.select(selector)
        print(f"  - {selector}: {len(found)} 项")
    
    # 查找所有div元素，看看页面结构
    print("\n2. 主要div结构：")
    divs = soup.find_all('div', class_=True)[:20]
    for div in divs:
        print(f"  - {div.name} class='{div.get('class')}'")
    
    # 查找分页相关元素
    print("\n3. 分页相关元素：")
    
    # 查找所有a标签
    print("\n4. 所有a标签（含href）：")
    a_tags = soup.find_all('a', href=True)[:30]
    for a in a_tags:
        href = a.get('href')
        text = a.text.strip()
        if href and ('page' in href or 'next' in text.lower() or '下一页' in text):
            print(f"  - {a.name} href='{href}' text='{text}'")
    
    # 查找pagination相关元素
    print("\n5. Pagination相关元素：")
    pagination = soup.find_all(['div', 'nav', 'ul'], class_=lambda x: x and ('pagination' in x.lower() or 'page' in x.lower()))
    for elem in pagination:
        print(f"  - {elem.name} class='{elem.get('class')}'")
        # 打印子元素
        for child in elem.children:
            if child.name:
                print(f"    - {child.name} class='{child.get('class')}' text='{child.text.strip()}'")
else:
    print(f"请求失败，状态码：{response.status_code}")