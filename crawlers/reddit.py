"""
Reddit 热门帖子爬虫
使用 Reddit JSON API (无需认证，附加 .json 即可)
子版块: r/programming, r/MachineLearning, r/artificial
"""
from typing import List, Dict
from .base import BaseCrawler

# Reddit 提供公开 JSON 接口，在任意 URL 后加 .json 即可
REDDIT_SUBREDDITS = ["programming", "MachineLearning", "artificial"]
REDDIT_BASE = "https://www.reddit.com/r/{sub}/hot.json"


class RedditCrawler(BaseCrawler):
    name = "reddit"
    display_name = "Reddit 热门"

    def fetch(self, max_items: int = 10) -> List[Dict]:
        items = []
        per_sub = max(3, max_items // len(REDDIT_SUBREDDITS))

        for sub in REDDIT_SUBREDDITS:
            if len(items) >= max_items:
                break
            try:
                resp = self._get(
                    REDDIT_BASE.format(sub=sub),
                    headers={
                        # Reddit 要求自定义 User-Agent
                        "User-Agent": "TechDigest/1.0 (by /u/example)",
                    },
                    params={"limit": per_sub + 2},
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"[Reddit] r/{sub} 请求失败: {e}")
                continue

            children = data.get("data", {}).get("children", [])
            for child in children:
                post = child.get("data", {})
                # 跳过置顶帖 (stickied)
                if post.get("stickied"):
                    continue

                pid = post.get("id", "")
                items.append({
                    "id": f"reddit-{pid}",
                    "title": post.get("title", ""),
                    "url": f"https://www.reddit.com{post.get('permalink', '')}",
                    "description": (post.get("selftext", "") or "")[:300],
                    "source": self.name,
                    "extra": {
                        "subreddit": f"r/{sub}",
                        "score": post.get("score", 0),
                        "comments": post.get("num_comments", 0),
                        "author": post.get("author", ""),
                    },
                })
                if len(items) >= max_items:
                    break

        return items[:max_items]
