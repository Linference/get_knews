"""
DeepSeek API 摘要模块
调用 DeepSeek Chat API，将爬取的条目批量转为中文核心功能概括

DeepSeek API 完全兼容 OpenAI SDK，只需修改 base_url 即可
"""
from typing import List, Dict
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

SYSTEM_PROMPT = """你是一个专业的技术摘要助手。你的任务是对给定的技术条目进行中文概括。

对每个条目，请用中文输出一行简洁的核心功能概括（不超过80字），重点突出：
- 这个项目/论文/文章是做什么的
- 核心技术点或创新点
- 为什么值得关注

输出格式：直接输出中文摘要，每行一条，与输入顺序一一对应。不要加序号，不要加前缀。"""


def summarize_items(items: List[Dict]) -> List[str]:
    """
    批量调用 DeepSeek API 对 items 进行中文摘要。
    返回与 items 等长的中文摘要列表。
    """
    if not items:
        return []

    # 构建输入文本
    lines = []
    for i, item in enumerate(items):
        parts = [f"[{i}] 标题: {item['title']}"]
        if item.get("description"):
            parts.append(f"描述: {item['description'][:300]}")
        if item.get("extra"):
            extra_str = ", ".join(f"{k}={v}" for k, v in item["extra"].items()
                                  if isinstance(v, (str, int, float)))
            if extra_str:
                parts.append(f"元数据: {extra_str}")
        lines.append(" | ".join(parts))

    user_content = "\n".join(lines)

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请对以下 {len(items)} 个技术条目逐一生成中文核心功能概括：\n\n{user_content}"},
            ],
            temperature=0.3,
            max_tokens=len(items) * 120,  # 每条约 120 tokens 足够
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[DeepSeek] API 调用失败: {e}")
        return ["[摘要生成失败]" for _ in items]

    # 按行拆分摘要
    summaries = [s.strip() for s in raw.split("\n") if s.strip()]

    # 去除非摘要行 (如序号、空行)
    import re
    summaries = [re.sub(r'^\[\d+\]\s*', '', s) for s in summaries]
    summaries = [re.sub(r'^\d+[\.\、\s]+', '', s) for s in summaries]

    # 补齐或截断
    while len(summaries) < len(items):
        summaries.append("[摘要缺失]")
    summaries = summaries[:len(items)]

    return summaries


def summarize_single(text: str, item_type: str = "技术内容") -> str:
    """对单个文本生成中文摘要"""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": f"你是技术摘要助手，将{item_type}转为中文核心概括 (≤120字)。"},
                {"role": "user", "content": text},
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[DeepSeek] 单条摘要失败: {e}")
        return "[摘要生成失败]"
