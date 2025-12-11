# 新闻分析系统

一个基于Django的新闻分析系统，支持新闻爬取、情感分析、关键词提取、数据可视化、评论、点赞和收藏等功能。

## 技术栈

- 后端框架: Django 5.2.9
- 数据库: SQLite (默认) / MySQL
- 新闻爬取: Playwright
- 情感分析: SnowNLP + 自定义分析器
- 关键词提取: Jieba + TF-IDF
- 数据可视化: ECharts
- 数据处理: NumPy + SciPy + scikit-learn

## 环境要求

- Python 3.8+
- pip 20.0+
- Node.js 14+ (可选，用于前端资源构建)

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/xxxiaoge613/Django.git
cd Django
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

> 注：如果安装过程中遇到问题，可以尝试升级pip后重试：
> ```bash
> pip install --upgrade pip
> ```

### 4. 安装Playwright浏览器

```bash
playwright install
```

### 5. 数据库迁移

```bash
python manage.py migrate
```

### 6. 创建超级用户

```bash
python manage.py createsuperuser
```

按照提示输入用户名、邮箱和密码。

## 配置说明

### 1. 基本配置

项目的主要配置文件位于 `DjangoProject/settings.py`，可以根据需要修改以下配置：

- `DEBUG`: 开发环境设为True，生产环境设为False
- `ALLOWED_HOSTS`: 允许访问的主机名列表
- `DATABASES`: 数据库配置
- `STATIC_URL`: 静态文件URL
- `MEDIA_URL` 和 `MEDIA_ROOT`: 媒体文件配置
- `TIME_ZONE`: 时区配置（默认：Asia/Shanghai）

### 2. 爬取配置

新闻爬取相关配置位于 `news_analysis/spiders/` 目录下的各个爬虫文件中，可以修改：

- 爬取间隔时间
- 爬取目标网站
- 爬取规则
- 数据解析规则

主要爬虫文件：
- `base_spider.py`: 基础爬虫类，定义了通用爬取逻辑
- `pai_com_spider.py`: 电商派新闻爬虫
- `quantum_bit_spider.py`: 量子位爬虫
- `thirty_six_kr_spider.py`: 36氪爬虫
- `spider_manager.py`: 爬虫管理器，用于协调多个爬虫

### 3. 情感分析配置

情感分析配置位于 `news_analysis/sentiment_analysis/analyzer.py` 中，可以调整：

- 情感分析阈值（正面、负面、中性的判断标准）
- 情感分类规则
- 分析模型参数

### 4. 数据清洗配置

数据清洗配置位于 `news_analysis/data_cleaning/cleaner.py` 中，可以调整：

- 清洗规则
- 过滤条件
- 数据标准化规则

## 运行方法

### 1. 启动开发服务器

```bash
python manage.py runserver
```

服务器将在 `http://127.0.0.1:8000/` 启动。

### 2. 运行爬虫

#### 运行所有爬虫

```bash
python manage.py runspiders
```

```bash
python run_spiders.py
```

#### 运行指定平台爬虫

```bash
python manage.py runspiders --platform 36kr
```

支持的平台：
- `36kr`: 36氪
- `quantum_bit`: 量子位

#### 启动定时爬取

```bash
python manage.py runspiders --scheduled --interval 3600
```

- `--scheduled`: 启用定时爬取
- `--interval`: 爬取间隔时间（秒），默认3600秒

### 3. 运行数据分析命令

#### 分析情感

```bash
python manage.py analyzesentiment
```

对所有未分析的新闻进行情感分析。

#### 清洗数据

```bash
python manage.py cleandata
```

对爬取的新闻数据进行清洗和标准化。

#### 更新36氪新闻

```bash
python manage.py update_36kr_news
```

专门更新36氪新闻数据。

#### 清空36氪新闻

```bash
python manage.py clear_36kr_news
```

清空所有36氪新闻数据（谨慎使用）。

## 主要功能

### 1. 新闻爬取

- 支持多个平台新闻自动爬取
- 支持定时爬取和手动爬取
- 支持指定平台爬取
- 自动处理网页解析和数据提取

### 2. 数据清洗

- 自动清洗爬取的新闻数据
- 去除重复内容
- 标准化数据格式
- 过滤无效数据

### 3. 情感分析

- 基于SnowNLP的情感分析
- 支持正面、负面、中性三类情感分类
- 自动计算情感得分
- 支持批量分析

### 4. 关键词提取

- 基于Jieba和TF-IDF的关键词提取
- 自动计算关键词权重
- 支持批量提取
- 关键词可视化展示

### 5. 数据可视化

- 情感趋势图：展示不同时间段的新闻情感分布
- 关键词云：可视化新闻关键词的出现频率
- 平台分布：展示不同来源平台的新闻数量
- 新闻列表：按时间、情感、关键词等条件筛选新闻

### 6. 用户功能

- 用户注册、登录和注销
- 个人资料管理
- 新闻评论和回复
- 新闻点赞
- 新闻收藏和标签管理

### 7. 内容管理

- 后台管理界面
- 新闻内容审核
- 评论管理
- 数据统计和分析

## 项目结构

```
DjangoProject/
├── DjangoProject/          # 项目配置目录
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── news_analysis/          # 新闻分析应用
│   ├── data_cleaning/      # 数据清洗模块
│   │   └── cleaner.py
│   ├── forms/              # 表单定义
│   │   └── auth_forms.py
│   ├── management/         # 自定义管理命令
│   │   └── commands/
│   │       ├── analyzesentiment.py
│   │       ├── cleandata.py
│   │       ├── clear_36kr_news.py
│   │       ├── runspiders.py
│   │       └── update_36kr_news.py
│   ├── middleware/         # 中间件
│   │   └── register_rate_limit.py
│   ├── migrations/         # 数据库迁移文件
│   ├── sentiment_analysis/ # 情感分析模块
│   │   └── analyzer.py
│   ├── spiders/            # 爬虫模块
│   │   ├── base_spider.py
│   │   ├── pai_com_spider.py
│   │   ├── quantum_bit_spider.py
│   │   ├── spider_manager.py
│   │   └── thirty_six_kr_spider.py
│   ├── utils/              # 工具函数
│   │   └── keyword_extractor.py
│   ├── views/              # 视图函数
│   │   ├── __init__.py
│   │   ├── auth_views.py
│   │   ├── news_views.py
│   │   ├── profile_views.py
│   │   └── visualization_views.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py           # 数据模型
│   ├── tests.py            # 测试文件
│   └── urls.py             # 应用URL配置
├── templates/              # HTML模板
│   ├── auth/               # 认证相关模板
│   │   ├── login.html
│   │   └── register.html
│   ├── base/               # 基础模板
│   │   └── base.html
│   ├── news/               # 新闻相关模板
│   │   ├── collections.html
│   │   ├── news_detail.html
│   │   └── news_list.html
│   ├── profile/            # 用户资料模板
│   │   ├── collections.html
│   │   ├── comments.html
│   │   ├── edit_comment.html
│   │   └── index.html
│   ├── visualization/      # 可视化模板
│   │   ├── dashboard.html
│   │   ├── keyword_cloud.html
│   │   ├── platform_distribution.html
│   │   └── sentiment_trend.html
│   ├── base.html
│   └── home.html
├── .gitignore              # Git忽略文件
├── manage.py               # Django管理命令入口
├── pyproject.toml          # Python项目配置
├── README.md               # 项目说明文档
└── requirements.txt        # 项目依赖
```

## 开发指南

### 1. 创建新的爬虫

在 `news_analysis/spiders/` 目录下创建新的爬虫类，继承自 `BaseSpider`，并实现以下方法：

```python
from news_analysis.spiders.base_spider import BaseSpider

class NewSpider(BaseSpider):
    platform_name = "new_platform"  # 平台名称
    start_urls = ["https://example.com/news"]  # 起始URL
    
    def parse_news_list(self, page_source):
        # 解析新闻列表页面，返回新闻详情页URL列表
        pass
    
    def parse_news_detail(self, page_source, url):
        # 解析新闻详情页，返回新闻数据字典
        pass
```

### 2. 扩展情感分析功能

修改 `news_analysis/sentiment_analysis/analyzer.py` 文件，添加新的情感分析规则或调整现有规则：

```python
def analyze_sentiment(self, text):
    # 情感分析逻辑
    # 可以添加自定义的情感词库或规则
    pass
```

### 3. 添加新的数据清洗规则

修改 `news_analysis/data_cleaning/cleaner.py` 文件，添加新的数据清洗规则：

```python
def clean_news(self, news):
    # 数据清洗逻辑
    # 可以添加自定义的清洗规则
    pass
```

### 4. 添加新的可视化图表

在 `templates/visualization/` 目录下创建新的模板文件，使用ECharts实现数据可视化：

```html
{% extends 'base/base.html' %}

{% block content %}
<div class="visualization-container">
    <h2>新图表标题</h2>
    <div id="chart" style="width: 100%; height: 400px;"></div>
</div>

<script type="text/javascript">
    // ECharts配置代码
    var myChart = echarts.init(document.getElementById('chart'));
    var option = {
        // 图表配置
    };
    myChart.setOption(option);
</script>
{% endblock %}
```

### 5. 添加新的管理命令

在 `news_analysis/management/commands/` 目录下创建新的命令文件：

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '新命令的描述'
    
    def add_arguments(self, parser):
        # 添加命令行参数
        pass
    
    def handle(self, *args, **options):
        # 命令处理逻辑
        pass
```

## 常见问题解答

### Q: 爬取新闻时提示浏览器未安装？
A: 请确保已运行 `playwright install` 命令安装所需的浏览器。

### Q: 情感分析结果不准确？
A: 可以尝试调整 `analyzer.py` 中的情感分析阈值，或添加自定义的情感词库。

### Q: 关键词提取结果不理想？
A: 可以尝试调整关键词提取的参数，或添加自定义的停用词表。

### Q: 开发服务器无法启动？
A: 请检查是否有其他进程占用了8000端口，或尝试使用其他端口启动：
```bash
python manage.py runserver 8001
```

### Q: 数据库连接失败？
A: 请检查 `settings.py` 中的数据库配置是否正确，确保数据库服务已启动。

## 版本历史记录

### v2.0.0 (2025-12-11)
- 升级Django至5.2.9版本
- 替换Scrapy为Playwright爬虫
- 新增数据清洗模块
- 增强情感分析功能
- 新增用户评论和点赞功能
- 新增新闻收藏和标签管理
- 优化数据可视化界面
- 完善后台管理功能

### v1.0.0 (2024-06-01)
- 初始版本发布
- 支持基本的新闻爬取
- 实现情感分析功能
- 支持关键词提取
- 基础的数据可视化

## 贡献说明

欢迎提交Issue和Pull Request！

### 提交Pull Request前请确保：

1. 代码符合PEP 8规范
2. 添加了必要的测试
3. 更新了相关文档
4. 通过了所有测试
5. 描述清晰的提交信息

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: https://github.com/xxxiaoge613/Django/issues
- Email: your-email@example.com

---

感谢使用新闻分析系统！