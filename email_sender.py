"""
邮件发送模块 — 生成精美的 HTML 摘要邮件
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
from config import (
    EMAIL_SMTP_HOST, EMAIL_SMTP_PORT,
    EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER,
)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f7fa; margin: 0; padding: 20px; color: #333;
  }}
  .container {{
    max-width: 720px; margin: 0 auto; background: #fff;
    border-radius: 12px; box-shadow: 0 2px 16px rgba(0,0,0,0.08);
    overflow: hidden;
  }}
  .header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff; padding: 28px 32px; text-align: center;
  }}
  .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
  .header p {{ margin: 6px 0 0; opacity: 0.9; font-size: 14px; }}
  .section {{ padding: 20px 32px; }}
  .section-title {{
    font-size: 18px; font-weight: 700; color: #667eea;
    border-left: 4px solid #667eea; padding-left: 12px; margin: 0 0 16px;
  }}
  .item {{
    padding: 14px 0; border-bottom: 1px solid #eee;
  }}
  .item:last-child {{ border-bottom: none; }}
  .item-title {{
    font-size: 15px; font-weight: 600; margin: 0 0 6px;
  }}
  .item-title a {{
    color: #333; text-decoration: none;
  }}
  .item-title a:hover {{ color: #667eea; }}
  .item-summary {{
    font-size: 13px; color: #555; line-height: 1.6; margin: 4px 0;
    padding: 8px 12px; background: #f8f9ff; border-radius: 6px;
  }}
  .item-meta {{
    font-size: 12px; color: #999; margin-top: 4px;
  }}
  .item-meta span {{ margin-right: 12px; }}
  .footer {{
    text-align: center; padding: 20px; color: #aaa; font-size: 12px;
  }}
  .tag {{
    display: inline-block; padding: 2px 8px; border-radius: 10px;
    background: #eef0ff; color: #667eea; font-size: 11px; margin-right: 4px;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📡 Tech Digest 每日科技速递</h1>
    <p>{date_str} · 由 DeepSeek AI 智能摘要</p>
  </div>
  {sections}
  <div class="footer">
    本邮件由 Tech Digest 自动生成 · 每日 {hour}:{minute:02d} 发送<br>
    Powered by DeepSeek API
  </div>
</div>
</body>
</html>"""

SECTION_TEMPLATE = """
<div class="section">
  <h2 class="section-title">{source_label}</h2>
  {items_html}
</div>"""

ITEM_TEMPLATE = """
<div class="item">
  <p class="item-title"><a href="{url}" target="_blank">{title}</a></p>
  <p class="item-summary">💡 {summary}</p>
  {meta_html}
</div>"""


def build_html(sections_data: List[Dict], hour: int = 9, minute: int = 0) -> str:
    """构建 HTML 邮件正文"""
    date_str = datetime.now().strftime("%Y年%m月%d日")
    sections_html = ""

    for section in sections_data:
        items_html = ""
        for item in section["items"]:
            meta_parts = []
            extra = item.get("extra", {})
            if "stars" in extra:
                meta_parts.append(f"<span>⭐ {extra['stars']:,}</span>")
            if "language" in extra:
                meta_parts.append(f'<span class="tag">{extra["language"]}</span>')
            if "score" in extra:
                meta_parts.append(f"<span>👍 {extra['score']}</span>")
            if "authors" in extra:
                authors = ", ".join(extra["authors"][:3])
                meta_parts.append(f"<span>👤 {authors}</span>")
            if "hot_score" in extra:
                meta_parts.append(f"<span>🔥 {extra['hot_score']}</span>")

            meta_html = f'<p class="item-meta">{"".join(meta_parts)}</p>' if meta_parts else ""

            items_html += ITEM_TEMPLATE.format(
                url=item.get("url", "#"),
                title=item.get("title", ""),
                summary=item.get("summary", ""),
                meta_html=meta_html,
            )

        sections_html += SECTION_TEMPLATE.format(
            source_label=section.get("label", ""),
            items_html=items_html,
        )

    return HTML_TEMPLATE.format(
        date_str=date_str,
        sections=sections_html,
        hour=hour,
        minute=minute,
    )


def send_digest(sections_data: List[Dict], hour: int = 9, minute: int = 0):
    """发送每日摘要邮件"""
    html = build_html(sections_data, hour, minute)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📡 Tech Digest · {datetime.now().strftime('%Y-%m-%d')}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"[邮件] 发送成功 → {EMAIL_RECEIVER}")
        return True
    except Exception as e:
        print(f"[邮件] 发送失败: {e}")
        return False
