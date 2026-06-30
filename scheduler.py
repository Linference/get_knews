"""
定时调度模块
使用 APScheduler 实现每日定时抓取 + 邮件推送
也可作为独立的后台进程长期运行
"""
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config import SCHEDULE_HOUR, SCHEDULE_MINUTE
from main import run_daily_digest


def scheduled_job():
    """定时任务：每日执行一次"""
    print(f"\n{'='*50}")
    print(f"[调度] {datetime.now().isoformat()} — 开始执行每日摘要任务")
    try:
        run_daily_digest()
    except Exception as e:
        print(f"[调度] 任务执行失败: {e}")
    print(f"[调度] 任务结束\n")


def start_scheduler():
    """启动定时调度器（阻塞运行）"""
    print(f"⏰ Tech Digest 调度器已启动")
    print(f"   每日 {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} 自动抓取并发送")
    print(f"   按 Ctrl+C 停止\n")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        scheduled_job,
        trigger=CronTrigger(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE),
        id="daily_digest",
        name="每日科技摘要",
        replace_existing=True,
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[调度] 已停止")


if __name__ == "__main__":
    start_scheduler()
