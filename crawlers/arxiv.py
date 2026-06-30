"""
arXiv 最新论文爬虫
使用 arXiv 官方 API (无需 key)
筛选 cs.AI / cs.CL / cs.CV 等计算机科学分类
"""
from typing import List, Dict
import feedparser
from .base import BaseCrawler


ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.SE"]


class ArXivCrawler(BaseCrawler):
    name = "arxiv"
    display_name = "arXiv Papers"

    def fetch(self, max_items: int = 10) -> List[Dict]:
        # 构建搜索 URL: 最近更新的 AI/ML 论文
        cats = "+OR+".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
        url = (
            f"http://export.arxiv.org/api/query?"
            f"search_query={cats}&sortBy=submittedDate&sortOrder=descending"
            f"&max_results={max_items}"
        )

        try:
            resp = self._get(url)
            resp.raise_for_status()
        except Exception as e:
            print(f"[arXiv] 请求失败: {e}")
            return []

        feed = feedparser.parse(resp.text)
        items = []
        for entry in feed.entries:
            arxiv_id = entry.id.split("/abs/")[-1]
            # 提取作者列表
            authors = [a.get("name", "") for a in entry.get("authors", [])]
            items.append({
                "id": f"arxiv-{arxiv_id}",
                "title": entry.get("title", "").strip().replace("\n", " "),
                "url": entry.get("link", ""),
                "description": entry.get("summary", "").strip().replace("\n", " ")[:500],
                "source": self.name,
                "extra": {
                    "authors": authors[:5],  # 最多 5 位作者
                    "published": entry.get("published", ""),
                    "categories": [t.get("term", "") for t in entry.get("tags", [])],
                },
            })
        return items
