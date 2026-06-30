"""
Hacker News 热门内容爬虫
使用 HN Firebase API (免费, 无需认证)
"""
from typing import List, Dict, Any
from .base import BaseCrawler


HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"


class HackerNewsCrawler(BaseCrawler):
    name = "hackernews"
    display_name = "Hacker News"

    def fetch(self, max_items: int = 10) -> List[Dict]:
        try:
            # 1. 获取热门 story ID 列表
            resp = self._get(HN_TOP_STORIES)
            resp.raise_for_status()
            story_ids = resp.json()[:max_items * 2]  # 多取一些，有的可能没有 url
        except Exception as e:
            print(f"[HN] 获取列表失败: {e}")
            return []

        # 2. 逐个获取 story 详情
        items = []
        for sid in story_ids:
            if len(items) >= max_items:
                break
            try:
                story = self._get(HN_ITEM.format(sid)).json()
            except Exception:
                continue

            # 跳过非 story 或没有链接的条目
            if story is None or story.get("type") != "story":
                continue
            url = story.get("url", "")
            if not url:
                # 无外链的 Ask HN / Show HN 用 HN 自身链接
                url = f"https://news.ycombinator.com/item?id={sid}"

            items.append({
                "id": f"hn-{sid}",
                "title": story.get("title", ""),
                "url": url,
                "description": story.get("text", "")[:500] if story.get("text") else "",
                "source": self.name,
                "extra": {
                    "score": story.get("score", 0),
                    "by": story.get("by", ""),
                    "descendants": story.get("descendants", 0),
                },
            })
        return items
