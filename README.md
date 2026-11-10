# Today News（个人新闻聚合与展示）

> 一个以 Python 为基础的新闻采集、存储和网页展示项目。本文档说明现有代码结构、运行方式和接口安全要求。

## 1. 项目简介

项目通过爬虫采集新闻或文章信息，将整理后的内容保存到数据库，再通过 Flask 页面进行展示。README 中描述的原始数据来源包括今日头条和搜狗微信；当前实际启用的数据源应以 `spiders/` 目录中的代码为准。

基本流程：

```text
新闻源 -> 爬虫采集 -> 字段解析 -> 数据库存储 -> Flask 页面展示
```

## 2. 技术组成

- Python：项目运行语言。
- Flask：Web 服务和路由。
- Requests：HTTP 请求（按爬虫实现使用）。
- Scrapy Selector：HTML/XML 内容解析。
- Peewee：数据库 ORM。
- SQLite 或其他 Peewee 支持的数据库：以 `models.py` 实际配置为准。

## 3. 主要文件和目录

| 路径 | 用途 |
|---|---|
| `run.py` | 创建 Flask 应用并注册路由 |
| `views.py` | 首页展示和爬虫触发接口 |
| `models.py` | 数据模型和数据库操作 |
| `spiders/` | 各新闻来源的采集逻辑 |
| `templates/` | Flask 页面模板 |
| `static/`、`images/` | 静态资源和图片 |
| `requirements.txt` 或 `requirement.txt` | Python 依赖文件，安装时以仓库实际文件名为准 |

## 4. 现有接口

| 路径 | 方法 | 用途 |
|---|---|---|
| `/` | GET | 新闻首页，支持分页和标签筛选 |
| `/crawl` | GET | 触发爬虫采集任务 |

注意：`/crawl` 会触发后台采集，不应向公网匿名开放。安全整改版本要求通过 `Authorization: Bearer <CRAWL_API_TOKEN>` 进行验证；没有配置令牌时接口应默认关闭。

## 5. 安装和运行

先确认 Python 版本和仓库中的依赖文件名称，然后执行：

```bash
python -m venv .venv
```

Windows PowerShell：
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux：
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

如果仓库中的依赖文件实际名称为 `requirement.txt`，请将命令中的文件名替换为该名称。

启动开发服务：
```bash
python run.py
```

本地访问 `http://127.0.0.1:5000/`。生产环境不要使用 Flask 自带开发服务器，应使用正式 WSGI 服务器并部署在 HTTPS 反向代理之后。

## 6. 触发爬虫接口的安全配置

在服务器环境变量中设置独立随机令牌：

```bash
export CRAWL_API_TOKEN='替换为足够长的随机值'
```

调用示例：

```bash
curl -X GET http://127.0.0.1:5000/crawl \\
  -H "Authorization: Bearer $CRAWL_API_TOKEN"
```

- 未配置令牌：接口返回 503，默认禁用。
- 未提供或令牌错误：接口返回 401。
- 令牌正确：才会启动爬虫任务。

真实令牌不能写入源码、README、Git 提交或公开日志。

## 7. 数据处理流程

1. 爬虫从新闻源获取页面或 API 数据。
2. 解析标题、文章地址、来源、摘要、标签、发布时间和图片。
3. 调用模型工具类将文章写入数据库。
4. 首页视图按发布时间倒序读取数据。
5. 页面按分页或标签条件展示新闻。

第三方页面结构可能变化，采集字段可能缺失。修改爬虫后应检查解析结果和数据库写入结果。

## 8. 常见问题

**首页没有数据**
- 检查数据库是否初始化。
- 检查爬虫是否成功执行。
- 检查新闻源是否变化或限制请求。
- 检查模板是否使用了正确字段。

**/crawl 返回 503**
- 尚未设置 `CRAWL_API_TOKEN`，需要在服务环境中配置。

**/crawl 返回 401**
- 检查请求是否包含 `Authorization: Bearer ...`。
- 检查客户端和服务端使用的令牌是否一致。

**图片无法显示**
- 新闻源图片链接可能过期。
- 检查图片是否已下载到本地静态目录。
- 检查模板中引用的静态路径。

## 9. 生产环境安全

- 关闭 Flask Debug。
- 使用正式 WSGI 服务。
- 使用 HTTPS。
- 限制爬虫触发接口访问权限和频率。
- 不要将数据库、Cookie、访问令牌或日志提交到公开仓库。
- 定期备份数据库和本地图片。
