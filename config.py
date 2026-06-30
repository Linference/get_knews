"""
Tech Digest — 全量配置文件
复制此文件为 config.py 并填入你的实际配置
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str = "") -> str:
    """读取环境变量，为空时回退到默认值（解决 GitHub Secrets 空值问题）"""
    val = os.getenv(key)
    return val if val else default


# ============================================
# DeepSeek API 配置
# ============================================
DEEPSEEK_API_KEY = _env("DEEPSEEK_API_KEY", "your-deepseek-api-key")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"  # 也可用 deepseek-reasoner (R1)

# ============================================
# 邮件配置 (SMTP) — 全部可选，不配则跳过发邮件
# ============================================
EMAIL_ENABLED = bool(_env("EMAIL_SMTP_HOST") and _env("EMAIL_PASSWORD"))
EMAIL_SMTP_HOST = _env("EMAIL_SMTP_HOST", "smtp.qq.com")
EMAIL_SMTP_PORT = int(_env("EMAIL_SMTP_PORT") or "587")
EMAIL_SENDER = _env("EMAIL_SENDER", "your-email@qq.com")
EMAIL_PASSWORD = _env("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = _env("EMAIL_RECEIVER", "receiver@example.com")

# ============================================
# 爬取源开关
# ============================================
SOURCES = {
    "github": True,      # GitHub Trending 今日热门仓库
    "arxiv": True,       # arXiv 最新 AI/CS 论文
    "hackernews": True,  # Hacker News 首页热门
    "reddit": True,      # Reddit r/programming 等热门帖子
    "zhihu": False,      # 知乎热榜 (国内源，默认关闭)
}

# 每个源最大抓取条数
MAX_ITEMS_PER_SOURCE = 10

# ============================================
# 调度配置
# ============================================
# 每日推送时间 (24小时制)
SCHEDULE_HOUR = 9     # 早上 9 点
SCHEDULE_MINUTE = 0

# ============================================
# 数据存储
# ============================================
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "digest.db")

# ============================================
# GitHub Pages 导出
# ============================================
# 抓取完成后自动生成 data/feed.json 供前端展示
FEED_JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "feed.json")

# ============================================
# 请求配置
# ============================================
REQUEST_TIMEOUT = 30  # 秒
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
