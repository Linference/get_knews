"""
GitHub Trending 爬虫
使用 GitHub API: https://api.github.com/search/repositories
按 stars 排序，抓取近期热门仓库
"""
from typing import List, Dict
from datetime import datetime, timedelta
from .base import BaseCrawler


class GitHubCrawler(BaseCrawler):
    name = "github"
    display_name = "GitHub Trending"

    def fetch(self, max_items: int = 10) -> List[Dict]:
        # 搜索最近 7 天创建的热门仓库
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"created:>={seven_days_ago}",
            "sort": "stars",
            "order": "desc",
            "per_page": max_items,
        }

        try:
            resp = self._get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[GitHub] 请求失败: {e}")
            return []

        items = []
        for repo in data.get("items", []):
            items.append({
                "id": f"github-{repo['id']}",
                "title": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "description": repo.get("description") or "",
                "source": self.name,
                "extra": {
                    "stars": repo.get("stargazers_count", 0),
                    "language": repo.get("language") or "Unknown",
                    "forks": repo.get("forks_count", 0),
                    "topics": repo.get("topics", []),
                },
            })
        return items
