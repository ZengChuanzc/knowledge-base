"""
文章过滤模块。

两阶段过滤：
  第一阶段 — 关键词快筛（零成本，快速剔除无关内容）
  第二阶段 — AI 语义过滤 + 热点评分（调用 LLM，分批处理）

设计：
  - 快筛阶段仅作关键词匹配，无 API 调用
  - 慢筛阶段将多篇文章分批（每批最多 30 篇），避免超出 Token 限制
  - 最终返回 Top N 篇（由 config.yaml 的 max_articles_per_day 控制）
"""

import json
import re
from typing import Optional

from config import get_config
from logger import get_logger
from models.article import RawArticle, ScoredArticle

logger = get_logger("filter")

# 每批最大文章数（避免超出 LLM 上下文窗口）
BATCH_SIZE = 30


def keyword_filter(articles: list[RawArticle]) -> list[RawArticle]:
    """
    第一阶段：关键词快速预过滤。

    规则：
      1. 标题或摘要包含 include 关键词中任一 -> 保留
      2. 包含 exclude 关键词中任一 -> 丢弃
      3. 大小写不敏感
      4. 严格模式：不包含任何 include 关键词的丢弃
    """
    config = get_config().keywords
    include_keywords = [k.lower() for k in config.include]
    exclude_keywords = [k.lower() for k in config.exclude]

    passed = []
    dropped_include = 0
    dropped_exclude = 0

    for article in articles:
        text = f"{article.title} {article.summary}".lower()

        # 排除检查
        if any(kw in text for kw in exclude_keywords):
            dropped_exclude += 1
            continue

        # 包含检查（严格模式：必须匹配至少一个 include 关键词）
        if any(kw in text for kw in include_keywords):
            passed.append(article)
        else:
            dropped_include += 1

    kept = len(passed)
    logger.info(
        "[SEARCH] 关键词过滤: %d -> %d 篇 "
        "(排除 %d 篇, 不相关 %d 篇)",
        len(articles), kept, dropped_exclude, dropped_include,
    )
    return passed


def build_score_prompt(articles: list[RawArticle]) -> str:
    """
    构建单批评分的 Prompt。

    每批最多 BATCH_SIZE 篇，让 LLM 一次性评分。
    """
    prompt_parts = [
        "# 任务：技术文章热点评分\n\n",
        "请对以下技术文章进行评分（0-100分），评分维度：\n",
        "1. **热度**（20分）：当前社区关注度\n",
        "2. **Java后端相关性**（25分）：与 Java/Spring/微服务等技术栈相关程度\n",
        "3. **AI相关性**（20分）：与 AI/LLM/Agent/MCP 等主题相关\n",
        "4. **工程价值**（20分）：对实际工程实践的指导意义\n",
        "5. **博客读者适配度**（15分）：是否适合技术博客读者\n\n",
        "输出格式（严格 JSON，不要包含其他文字）：\n",
        '{"scores": [\n',
        '  {"index": 0, "score": 85, "reason": "...", "should_keep": true},\n',
        '  {"index": 1, "score": 30, "reason": "...", "should_keep": false}\n',
        "]}\n\n",
        "**要求**：\n",
        "- 评分 0-100 整数\n",
        "- should_keep=false 表示不相关/无价值\n",
        "- should_keep=true 且评分 >= 60 的才保留\n",
        "- 评分理由用中文，一句话\n\n",
        "---\n\n",
    ]

    for i, article in enumerate(articles):
        prompt_parts.append(f"## 文章 #{i}\n")
        prompt_parts.append(f"- **标题**: {article.title}\n")
        prompt_parts.append(f"- **来源**: {article.source}\n")
        prompt_parts.append(f"- **摘要**: {article.summary[:500]}\n")
        prompt_parts.append(f"- **语言**: {article.lang}\n\n")

    return "".join(prompt_parts)


def parse_score_response(response: str,
                         articles: list[RawArticle]) -> list[ScoredArticle]:
    """
    解析 LLM 评分响应，返回 ScoredArticle 列表。
    多种解析策略容错。
    """
    # 清理响应：移除可能的 markdown 代码块标记
    cleaned = response.strip()

    # 策略1：从 ```json ... ``` 中提取
    json_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL
    )
    if json_match:
        json_str = json_match.group(1)
    else:
        # 策略2：尝试直接解析整个响应
        json_str = cleaned

    # 策略3：找第一个 { 和最后一个 }
    start = json_str.find("{")
    end = json_str.rfind("}")
    if start != -1 and end != -1 and end > start:
        json_str = json_str[start:end + 1]
    else:
        logger.error("[ERR] LLM 响应不包含 JSON 结构")
        logger.debug("原始响应前200字符: %s", cleaned[:200])
        return []

    # 解析 JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error("[ERR] JSON 解析失败: %s", e)
        logger.debug("尝试解析的 JSON 字符串: %s", json_str[:300])
        return []

    scores_data = data.get("scores", [])
    if not scores_data:
        logger.warning("[WARN] LLM 返回的 scores 为空")
        return []

    scored: list[ScoredArticle] = []
    for entry in scores_data:
        idx = entry.get("index")
        if idx is None or idx >= len(articles):
            continue
        article = articles[idx]
        scored.append(ScoredArticle(
            **article.model_dump(),
            score=entry.get("score", 0),
            score_reason=entry.get("reason", ""),
        ))

    return scored


async def ai_score_filter(articles: list[RawArticle],
                          llm_func) -> list[ScoredArticle]:
    """
    第二阶段：AI 语义过滤 + 热点评分。

    分批处理，每批 BATCH_SIZE 篇，合并结果后返回 Top N。
    """
    if not articles:
        return []

    config = get_config()
    max_count = config.output.max_articles_per_day
    total = len(articles)

    logger.info("[AI] AI 评分阶段: %d 篇候选（每批 %d 篇）", total, BATCH_SIZE)

    all_scored: list[ScoredArticle] = []

    # 分批处理
    for batch_start in range(0, total, BATCH_SIZE):
        batch = articles[batch_start:batch_start + BATCH_SIZE]
        batch_end = min(batch_start + BATCH_SIZE, total)
        logger.info("[AI] 评分批次 %d-%d / %d ...", batch_start + 1, batch_end, total)

        try:
            prompt = build_score_prompt(batch)
            response = await llm_func(prompt)
            scored = parse_score_response(response, batch)
            all_scored.extend(scored)
        except Exception as e:
            logger.error("[ERR] 批次评分失败 [%d-%d]: %s",
                         batch_start + 1, batch_end, e)
            continue

    if not all_scored:
        logger.warning("[WARN] AI 评分后没有合格文章")
        return []

    # 过滤低分 + 排序
    filtered = [s for s in all_scored
                if s.score >= 60 and s.score > 0]
    filtered.sort(key=lambda x: x.score, reverse=True)

    # 取 Top N
    top = filtered[:max_count * 2]  # 放宽一点让后续选择更多，但 main.py 会再截断

    for s in top[:max_count]:
        logger.info("[STAR] [%.0f分] %s -- %s",
                    s.score, s.title[:60], s.score_reason[:80])

    dropped = len(all_scored) - len(top)
    if dropped > 0:
        logger.info("[DOWN] AI 评分过滤: 移除 %d 篇低分文章", dropped)

    # 返回最多 max_count 篇
    return top[:max_count]
