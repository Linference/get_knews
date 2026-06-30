"""
Tech Digest — 全量配置文件
复制此文件为 config.py 并填入你的实际配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# DeepSeek API 配置
# ============================================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"  # 也可用 deepseek-reasoner (R1)

# ============================================
# 邮件配置 (SMTP)
# ============================================
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.qq.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your-email@qq.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-smtp-auth-code")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "receiver@example.com")

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
