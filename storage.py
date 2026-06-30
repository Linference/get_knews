"""
数据存储层 — SQLite 持久化
记录已抓取条目，用于去重和历史追踪
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT DEFAULT '',
                summary_cn TEXT DEFAULT '',
                extra_json TEXT DEFAULT '{}',
                fetched_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS digest_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sent_at TEXT NOT NULL,
                item_count INTEGER NOT NULL,
                sources TEXT NOT NULL,
                success INTEGER DEFAULT 1
            )
        """)
        conn.commit()


def is_new(item_id: str) -> bool:
    """检查条目是否未被收录过"""
    with get_connection() as conn:
        row = conn.execute("SELECT 1 FROM items WHERE id = ?", (item_id,)).fetchone()
        return row is None


def save_items(items: List[dict]):
    """批量保存新条目"""
    now = datetime.now().isoformat()
    with get_connection() as conn:
        for item in items:
            conn.execute(
                """INSERT OR IGNORE INTO items
                   (id, source, title, url, description, summary_cn, extra_json, fetched_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item["id"],
                    item.get("source", ""),
                    item.get("title", ""),
                    item.get("url", ""),
                    item.get("description", ""),
                    item.get("summary", ""),
                    json.dumps(item.get("extra", {}), ensure_ascii=False),
                    now,
                ),
            )
        conn.commit()


def log_digest(item_count: int, sources: List[str], success: bool = True):
    """记录一次摘要发送"""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO digest_log (sent_at, item_count, sources, success) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), item_count, ",".join(sources), int(success)),
        )
        conn.commit()


def get_recent_items(days: int = 7) -> List[dict]:
    """获取近 N 天已抓取的条目"""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM items WHERE fetched_at > datetime('now', ?) ORDER BY fetched_at DESC",
            (f"-{days} days",),
        ).fetchall()
        return [dict(r) for r in rows]
