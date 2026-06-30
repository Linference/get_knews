"""爬虫模块 — 统一注册入口"""
from .base import BaseCrawler
from .github import GitHubCrawler
from .arxiv import ArXivCrawler
from .hackernews import HackerNewsCrawler
from .zhihu import ZhihuCrawler
from .reddit import RedditCrawler

# 所有可用爬虫注册表
CRAWLER_REGISTRY = {
    "github": GitHubCrawler,
    "arxiv": ArXivCrawler,
    "hackernews": HackerNewsCrawler,
    "zhihu": ZhihuCrawler,
    "reddit": RedditCrawler,
}

__all__ = ["BaseCrawler", "CRAWLER_REGISTRY"]
