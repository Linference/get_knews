"""
Tech Digest — 主入口
编排整个流程：爬取 → 去重 → 摘要 → 导出 JSON → 邮件
"""
import sys
import json
import os
from datetime import datetime
from config import SOURCES, MAX_ITEMS_PER_SOURCE, SCHEDULE_HOUR, SCHEDULE_MINUTE, FEED_JSON_PATH
from crawlers import CRAWLER_REGISTRY
from summarizer import summarize_items
from storage import init_db, is_new, save_items, log_digest, get_recent_items
from email_sender import send_digest


def export_feed_json():
    """导出近 7 天的摘要数据为 JSON，供 GitHub Pages 前端使用"""
    items = get_recent_items(days=7)
    feed = []
    for item in items:
        feed.append({
            "id": item["id"],
            "source": item["source"],
            "title": item["title"],
            "url": item["url"],
            "description": item["description"],
            "summary": item["summary_cn"],
            "extra": json.loads(item["extra_json"]) if item["extra_json"] else {},
            "fetched_at": item["fetched_at"],
        })

    os.makedirs(os.path.dirname(FEED_JSON_PATH), exist_ok=True)
    with open(FEED_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "total": len(feed),
            "items": feed,
        }, f, ensure_ascii=False, indent=2)
    print(f"[导出] feed.json 已生成 ({len(feed)} 条)\n")


def run_daily_digest():
    """执行一次完整的每日摘要流程"""
    print(f"📡 Tech Digest — {datetime.now().isoformat()}\n")

    # 初始化数据库
    init_db()

    all_sections = []
    total_new = 0

    # 遍历所有启用的数据源
    for source_name, enabled in SOURCES.items():
        if not enabled:
            continue
        if source_name not in CRAWLER_REGISTRY:
            print(f"[跳过] 未知数据源: {source_name}")
            continue

        crawler_cls = CRAWLER_REGISTRY[source_name]
        crawler = crawler_cls()

        print(f"[抓取] {crawler.display_name} ...")
        items = crawler.fetch(max_items=MAX_ITEMS_PER_SOURCE)

        if not items:
            print(f"  └─ 无结果\n")
            continue

        # 去重：只保留未收录的条目
        new_items = [it for it in items if is_new(it["id"])]
        skipped = len(items) - len(new_items)
        print(f"  └─ 获取 {len(items)} 条, 新 {len(new_items)} 条, 跳过 {skipped} 条")

        if not new_items:
            print()
            continue

        # 调用 DeepSeek API 生成中文摘要
        print(f"[摘要] 调用 DeepSeek API 对 {len(new_items)} 条内容生成中文概括 ...")
        summaries = summarize_items(new_items)

        # 将摘要写入条目
        for item, summary in zip(new_items, summaries):
            item["summary"] = summary

        # 存入数据库
        save_items(new_items)
        total_new += len(new_items)

        # 构建邮件 section
        all_sections.append({
            "label": crawler.display_name,
            "source": source_name,
            "items": new_items,
        })
        print()

    # 导出 JSON 供 GitHub Pages 前端
    export_feed_json()

    if not all_sections:
        print("⚠️  没有新内容，跳过邮件发送")
        log_digest(0, [], success=True)
        return

    # 发送邮件
    print(f"[邮件] 生成 HTML 摘要 ({total_new} 条) ...")
    success = send_digest(all_sections, hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)

    # 记录日志
    sources_used = [s["source"] for s in all_sections]
    log_digest(total_new, sources_used, success=success)

    print(f"\n✅ 完成! 共 {total_new} 条新内容, {'邮件已发送' if success else '邮件发送失败'}")


def run_once(source: str = None, no_email: bool = False):
    """单次手动运行 (可指定来源, 可跳过邮件)"""
    if source:
        SOURCES.clear()
        SOURCES[source] = True

    init_db()

    all_sections = []
    total_new = 0

    for source_name, enabled in SOURCES.items():
        if not enabled or source_name not in CRAWLER_REGISTRY:
            continue

        crawler = CRAWLER_REGISTRY[source_name]()
        print(f"[抓取] {crawler.display_name} ...")
        items = crawler.fetch(max_items=MAX_ITEMS_PER_SOURCE)

        new_items = [it for it in items if is_new(it["id"])]
        print(f"  └─ 获取 {len(items)} 条, 新 {len(new_items)} 条")

        if not new_items:
            continue

        print(f"[摘要] DeepSeek API ...")
        summaries = summarize_items(new_items)
        for item, summary in zip(new_items, summaries):
            item["summary"] = summary

        save_items(new_items)
        total_new += len(new_items)

        all_sections.append({
            "label": crawler.display_name,
            "source": source_name,
            "items": new_items,
        })

    if all_sections:
        # 打印结果
        for section in all_sections:
            print(f"\n{'='*60}")
            print(f"  {section['label']}")
            print(f"{'='*60}")
            for item in section["items"]:
                print(f"  📌 {item['title']}")
                print(f"     💡 {item['summary']}")
                print(f"     🔗 {item['url']}")
                print()

        # 导出 JSON 供 GitHub Pages
        export_feed_json()

        if not no_email:
            send_digest(all_sections, hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)
            sources_used = [s["source"] for s in all_sections]
            log_digest(total_new, sources_used)

    print(f"\n✅ 共 {total_new} 条新内容")


# ============================================
# CLI 入口
# ============================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "once":
            src = sys.argv[2] if len(sys.argv) > 2 else None
            run_once(source=src)
        elif cmd == "once-no-email":
            src = sys.argv[2] if len(sys.argv) > 2 else None
            run_once(source=src, no_email=True)
        elif cmd == "schedule":
            from scheduler import start_scheduler
            start_scheduler()
        elif cmd == "sources":
            print("可用数据源:")
            for name, cls in CRAWLER_REGISTRY.items():
                enabled = "✓" if SOURCES.get(name) else "✗"
                print(f"  [{enabled}] {name} — {cls.display_name}")
        elif cmd == "help":
            print("""
Tech Digest — 科技资讯自动抓取 & DeepSeek 摘要 & 邮件推送

用法:
  python main.py once              # 单次运行，抓取所有源并发送邮件
  python main.py once github       # 只抓取指定源
  python main.py once-no-email     # 抓取但不发邮件 (终端查看)
  python main.py schedule          # 启动定时调度器 (后台每日运行)
  python main.py sources           # 查看所有可用数据源
  python main.py help              # 显示此帮助
            """)
        else:
            print(f"未知命令: {cmd}，请用 'python main.py help' 查看帮助")
    else:
        # 默认: 单次运行
        run_once()
