"""
爬虫基类 — 定义统一接口 & 通用工具方法
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import requests
from config import USER_AGENT, REQUEST_TIMEOUT


class BaseCrawler(ABC):
    """所有爬虫的抽象基类"""

    name: str = "base"          # 爬虫标识
    display_name: str = "Base"  # 展示名称

    def _get(self, url: str, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {})
        headers.setdefault("User-Agent", USER_AGENT)
        return requests.get(
            url, headers=headers,
            timeout=kwargs.pop("timeout", REQUEST_TIMEOUT),
            **kwargs,
        )

    @abstractmethod
    def fetch(self, max_items: int = 10) -> List[Dict]:
        """
        抓取条目列表。
        每条格式:
        {
            "id": "unique-id",
            "title": "原始标题",
            "url": "链接",
            "description": "原始描述 (可选)",
            "source": self.name,
            "extra": { ... }
        }
        """
        ...
