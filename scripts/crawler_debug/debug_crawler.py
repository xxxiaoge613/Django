import requests
from bs4 import BeautifulSoup

# 调试量子位网站

def debug_quantum_bit():
    print("\n\n=== 调试量子位网站 ===")
    url = 'https://www.qbitai.com/category/%e8%b5%84%e8%ae%af'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"页面标题: {soup.title.text if soup.title else 'None'}")
    print(f"页面内容前500字符: {response.text[:500]}...")
    
    # 检查所有h3和h2元素
    print("\n所有h3元素:")
    h3_tags = soup.find_all('h3')[:10]
    for i, tag in enumerate(h3_tags):
        print(f"h3[{i}]: {tag.text.strip() if tag.text else 'None'}")
        if tag.parent:
            print(f"  父元素: {tag.parent.name}.{tag.parent.get('class', [])}")
    
    # 检查所有article元素
    print("\n所有article元素:")
    articles = soup.find_all('article')[:10]
    for i, article in enumerate(articles):
        print(f"article[{i}] 内容: {article.text[:100]}...")
        print(f"article[{i}] 属性: {article.attrs}")

# 调试36氪网站

def debug_36kr():
    print("\n\n=== 调试36氪网站 ===")
    url = 'https://www.36kr.com/information/web_news/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"页面标题: {soup.title.text if soup.title else 'None'}")
    print(f"页面内容前500字符: {response.text[:500]}...")
    
    # 检查所有h3和h2元素
    print("\n所有h3元素:")
    h3_tags = soup.find_all('h3')[:10]
    for i, tag in enumerate(h3_tags):
        print(f"h3[{i}]: {tag.text.strip() if tag.text else 'None'}")
        if tag.parent:
            print(f"  父元素: {tag.parent.name}.{tag.parent.get('class', [])}")
    
    # 检查所有article或section元素
    print("\n所有article和section元素:")
    articles = soup.find_all(['article', 'section'])[:10]
    for i, article in enumerate(articles):
        print(f"element[{i}] 内容: {article.text[:100]}...")
        print(f"element[{i}] 属性: {article.attrs}")

if __name__ == "__main__":
    debug_quantum_bit()
    debug_36kr()
