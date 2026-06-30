# 📡 Tech Digest — 多源科技资讯自动抓取 + DeepSeek AI 中文摘要

[![Daily Tech Digest](https://github.com/Linference/get_knews/actions/workflows/crawl.yml/badge.svg)](https://github.com/Linference/get_knews/actions)

每天自动抓取 **GitHub Trending / Hacker News / arXiv / Reddit** 等顶级科技社区的热门内容，调用 **DeepSeek API** 生成中文核心功能概括，通过 **GitHub Pages** 网页 + **邮件** 双通道推送。

> 🔗 演示站点: `https://linference.github.io/get_knews`

---

## ✨ 功能特性

| 模块 | 说明 |
|------|------|
| 🌐 **多源爬取** | GitHub Trending、Hacker News、arXiv 论文、Reddit、知乎热榜 |
| 🤖 **AI 摘要** | DeepSeek API (deepseek-chat) 批量生成中文核心功能概括 |
| 📊 **网页展示** | GitHub Pages 静态站点，卡片式展示，支持按来源筛选 |
| 📧 **邮件推送** | 精美 HTML 邮件，每日定时发送到指定邮箱 |
| ⏰ **全自动** | GitHub Actions 每日定时运行，无需服务器 |
| 💾 **去重** | SQLite 持久化，避免重复推送 |

---

## 🚀 快速开始

### 1. Fork 本项目

点击右上角 **Fork**，把项目复制到你的 GitHub 账户下。

### 2. 配置 Secrets

在 Fork 后的仓库中，进入 **Settings → Secrets and variables → Actions**，添加以下 Secrets：

| Secret 名称 | 说明 | 必填 |
|-------------|------|:---:|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | ✅ 必填 |
| `EMAIL_SENDER` | 发件邮箱（自收自发时同收件邮箱） | 邮件用 |
| `EMAIL_PASSWORD` | SMTP 授权码（不是邮箱密码！） | 邮件用 |
| `EMAIL_RECEIVER` | 收件邮箱（自收自发时同发件邮箱） | 邮件用 |

> 💡 **获取 DeepSeek API Key**: 访问 [platform.deepseek.com](https://platform.deepseek.com) 注册并获取。
> 📧 邮件功能完全可选，不配也能正常运行（仅 GitHub Pages 展示）。

### 3. 启用 GitHub Pages

进入 **Settings → Pages**：
- **Source**: `GitHub Actions`

或者选 **Deploy from a branch**，分支选 `main`，目录选 `/docs`。

### 4. 手动触发一次测试

进入 **Actions → Daily Tech Digest → Run workflow**，点击运行。几分钟后你的 GitHub Pages 站点就会显示内容！

---

## 🖥️ 本地运行

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/tech_digest.git
cd tech_digest

# 2. 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key

# 4. 单次运行（终端查看结果，不发邮件）
python main.py once-no-email

# 5. 单次运行 + 发送邮件
python main.py once

# 6. 只抓取某个源
python main.py once github

# 7. 查看可用数据源
python main.py sources

# 8. 启动本地定时调度器（每日定时运行）
python main.py schedule
```

---

## 📁 项目结构

```
tech_digest/
├── .github/workflows/
│   └── crawl.yml            # GitHub Actions 全自动工作流
├── crawlers/
│   ├── __init__.py           # 爬虫注册表
│   ├── base.py               # 爬虫基类
│   ├── github.py             # GitHub Trending 爬虫
│   ├── hackernews.py         # Hacker News 爬虫
│   ├── arxiv.py              # arXiv 论文爬虫
│   ├── reddit.py             # Reddit 热门爬虫
│   └── zhihu.py              # 知乎热榜爬虫
├── docs/                     # GitHub Pages 前端
│   ├── index.html
│   ├── style.css
│   └── app.js
├── data/
│   └── feed.json             # 自动生成的摘要数据
├── main.py                   # 主入口 & CLI
├── summarizer.py             # DeepSeek API 摘要模块
├── storage.py                # SQLite 存储 & 去重
├── email_sender.py           # 邮件发送 (HTML 模板)
├── scheduler.py              # 本地定时调度
├── config.py                 # 全量配置
├── requirements.txt
└── .env.example              # 环境变量模板
```

---

## 🔧 自定义

### 开关数据源

编辑 `config.py`:

```python
SOURCES = {
    "github": True,
    "arxiv": True,
    "hackernews": True,
    "reddit": True,
    "zhihu": False,     # 国内源，按需开启
}
```

### 调整抓取数量 & 时间

```python
MAX_ITEMS_PER_SOURCE = 10   # 每个源最多抓几条
SCHEDULE_HOUR = 9           # 每日推送时间 (北京时间)
SCHEDULE_MINUTE = 0
```

### 切换 DeepSeek 模型

```python
DEEPSEEK_MODEL = "deepseek-chat"      # V3 (快速)
# DEEPSEEK_MODEL = "deepseek-reasoner"  # R1 (深度推理)
```

---

## 🤝 添加新数据源

1. 在 `crawlers/` 下创建新文件，继承 `BaseCrawler`
2. 实现 `fetch()` 方法，返回条目列表
3. 在 `crawlers/__init__.py` 注册
4. 在 `config.py` 的 `SOURCES` 中启用

---

## 📧 邮箱自收自发配置（QQ邮箱示例）

想让爬虫结果每天发到自己邮箱？以 QQ 邮箱为例：

### 1. 开启 SMTP 服务

登录 QQ 邮箱 → **设置 → 账户 → POP3/SMTP 服务** → 开启 → 按提示发送短信验证。

验证成功后会得到一个 **授权码**（一串字母），这就是 `EMAIL_PASSWORD`。

### 2. 添加 Secrets

在仓库 **Settings → Secrets and variables → Actions** 添加 3 个 Secret：

| Name | Value |
|------|-------|
| `EMAIL_SENDER` | `你的QQ号@qq.com` |
| `EMAIL_PASSWORD` | `授权码（不是QQ密码）` |
| `EMAIL_RECEIVER` | `你的QQ号@qq.com`（同一个） |

> 其他邮箱同理：163 用 `smtp.163.com`，Gmail 用 `smtp.gmail.com`，端口统一 `587`。

---

## 📄 License

MIT — 随意使用、修改和分发。
