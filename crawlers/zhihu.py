"""
知乎热榜爬虫 (简化版)
使用知乎热榜 API: https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total
"""
from typing import List, Dict
from .base import BaseCrawler


ZHIHU_HOT_URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
ZHIHU_ITEM_URL = "https://www.zhihu.com/question/{id}"


class ZhihuCrawler(BaseCrawler):
    name = "zhihu"
    display_name = "知乎热榜"

    def fetch(self, max_items: int = 10) -> List[Dict]:
        headers = {
            "Referer": "https://www.zhihu.com/hot",
            "Accept": "application/json",
        }
        try:
            resp = self._get(ZHIHU_HOT_URL, headers=headers, params={"limit": max_items})
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[知乎] 请求失败: {e}")
            return []

        items = []
        for entry in data.get("data", []):
            target = entry.get("target", {})
            qid = target.get("id", 0)
            items.append({
                "id": f"zhihu-{qid}",
                "title": target.get("title", ""),
                "url": ZHIHU_ITEM_URL.format(id=qid),
                "description": target.get("excerpt", "")[:300],
                "source": self.name,
                "extra": {
                    "hot_score": entry.get("detail_text", ""),
                    "answer_count": target.get("answer_count", 0),
                },
            })
        return items
