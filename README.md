# 新闻分析系统

一个基于Django的新闻分析系统，支持新闻爬取、情感分析、关键词提取和数据可视化。

## 技术栈

- 后端框架: Django 4.x
- 数据库: SQLite (默认) / MySQL
- 新闻爬取: Scrapy (整合在Django中)
- 情感分析: 自定义分析器
- 数据可视化: ECharts
- 关键词提取: 自定义提取器

## 环境要求

- Python 3.8+
- pip 20.0+

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

> 如果没有requirements.txt文件，可以手动安装主要依赖：
> ```bash
> pip install django requests beautifulsoup4 echarts-python
> ```

### 4. 数据库迁移

```bash
python manage.py migrate
```

### 5. 创建超级用户

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

### 2. 爬取配置

新闻爬取相关配置位于 `news_analysis/spiders/` 目录下的各个爬虫文件中，可以修改：

- 爬取频率
- 爬取目标网站
- 爬取规则

### 3. 情感分析配置

情感分析配置位于 `news_analysis/sentiment_analysis/analyzer.py` 中，可以调整：

- 情感分析阈值
- 情感分类规则

## 运行方法

### 1. 启动开发服务器

```bash
python manage.py runserver
```

服务器将在 `http://127.0.0.1:8000/` 启动。

### 2. 运行爬虫

```bash
python manage.py crawl <spider_name>
```

可用的爬虫名称：
- `pai_com_spider`: 爬取湃客新闻
- `quantum_bit_spider`: 爬取量子位
- `thirty_six_kr_spider`: 爬取36氪

### 3. 运行数据分析命令

```bash
python manage.py <command_name>
```

## 主要功能

### 1. 新闻爬取

自动从指定网站爬取新闻内容，包括标题、内容、发布时间、来源等信息。

### 2. 情感分析

对爬取的新闻进行情感分析，分为正面、负面和中性三类。

### 3. 关键词提取

从新闻内容中提取关键词，用于后续分析和可视化。

### 4. 数据可视化

- 情感趋势图：展示不同时间段的新闻情感分布
- 关键词云：可视化新闻关键词的出现频率
- 新闻列表：按时间、情感、关键词等条件筛选新闻

### 5. 用户管理

支持用户注册、登录和个人资料管理。

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
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── data_cleaning/      # 数据清洗模块
│   ├── management/         # 自定义管理命令
│   ├── migrations/         # 数据库迁移文件
│   ├── models.py           # 数据模型
│   ├── sentiment_analysis/ # 情感分析模块
│   ├── spiders/            # 爬虫模块
│   ├── tests.py            # 测试文件
│   ├── urls.py             # 应用URL配置
│   ├── utils/              # 工具函数
│   └── views.py            # 视图函数
├── templates/              # HTML模板
│   ├── auth/               # 认证相关模板
│   ├── base/               # 基础模板
│   ├── news/               # 新闻相关模板
│   ├── profile/            # 用户资料模板
│   └── visualization/      # 可视化模板
├── scripts/                # 脚本文件
│   ├── crawler_debug/      # 爬虫调试脚本
│   ├── data_analysis/      # 数据分析脚本
│   └── data_processing/    # 数据处理脚本
├── test/                   # 测试文件
├── manage.py               # Django管理命令入口
└── requirements.txt        # 项目依赖
```

## 开发指南

### 1. 创建新的爬虫

在 `news_analysis/spiders/` 目录下创建新的爬虫类，继承自 `BaseSpider`。

### 2. 扩展情感分析功能

修改 `news_analysis/sentiment_analysis/analyzer.py` 文件，添加新的情感分析规则。

### 3. 添加新的可视化图表

在 `templates/visualization/` 目录下创建新的模板文件，使用ECharts实现数据可视化。

## 贡献说明

欢迎提交Issue和Pull Request！

### 提交Pull Request前请确保：

1. 代码符合PEP 8规范
2. 添加了必要的测试
3. 更新了相关文档
4. 通过了所有测试

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: https://github.com/xxxiaoge613/Django/issues
- Email: your-email@example.com

---

感谢使用新闻分析系统！