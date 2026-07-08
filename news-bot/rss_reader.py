"""
RSS 抓取与解析模块。

职责：
  1. 遍历 config.yaml 中所有 RSS 源
  2. 使用 feedparser 解析 RSS/Atom
  3. 尝试通过 BeautifulSoup 抓取正文全文
  4. 标准化为 RawArticle 列表输出

设计：
  - 每个源独立抓取，单个失败不影响其他源
  - 支持 RSS 2.0 / Atom 两种格式
  - 自动处理编码问题
"""

import asyncio
from datetime import datetime
from typing import Optional

import feedparser
from bs4 import BeautifulSoup
from httpx import AsyncClient, HTTPError, TimeoutException

from config import get_config
from logger import get_logger
from models.article import RawArticle

logger = get_logger("rss_reader")

# ── HTTP 客户端配置 ───────────────────────────────────────────────────────────
TIMEOUT = 30  # 秒
USER_AGENT = (
    "Mozilla/5.0 (compatible; KnowledgeBaseBot/1.0; "
    "+https://github.com/zengchuanzc/knowledge-base)"
)


async def fetch_feed(url: str, session: AsyncClient) -> Optional[str]:
    """抓取 RSS feed 原始 XML 内容。"""
    try:
        resp = await session.get(url, timeout=TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except (HTTPError, TimeoutException) as e:
        logger.warning("[WARN] 抓取失败 [%s]: %s", url, e)
        return None


async def fetch_full_content(url: str, session: AsyncClient) -> str:
    """
    尝试抓取文章正文全文（HTML 正文提取）。
    返回纯文本格式。
    """
    try:
        resp = await session.get(url, timeout=TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # 移除脚本/样式等非正文元素
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # 优先 article 标签，再 fallback body
        article = soup.find("article") or soup.body
        if article:
            text = article.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # 限制长度，避免 Token 浪费
        return text[:8000]
    except Exception as e:
        logger.debug("正文抓取失败 [%s]: %s", url, e)
        return ""


def parse_entry(entry, source_name: str, source_url: str,
                lang: str) -> Optional[RawArticle]:
    """解析 feedparser 单条记录为 RawArticle。"""
    try:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            return None

        # 摘要（取 summary 或 description）
        summary = entry.get("summary", "") or entry.get("description", "") or ""
        # 去除 HTML 标签
        if summary:
            soup = BeautifulSoup(summary, "lxml")
            summary = soup.get_text(separator="\n", strip=True)[:1000]

        # 作者
        author = None
        if "author" in entry:
            author = entry.author
        elif "author_detail" in entry and "name" in entry.author_detail:
            author = entry.author_detail.name

        # 发布日期
        published = None
        if "published_parsed" in entry and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])
        elif "updated_parsed" in entry and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6])

        return RawArticle(
            title=title,
            url=link,
            summary=summary,
            author=author,
            published=published,
            source=source_name,
            source_url=source_url,
            lang=lang,
        )
    except Exception as e:
        logger.warning("⚠️  条目解析失败: %s", e)
        return None


async def fetch_and_parse_source(source: dict,
                                 session: AsyncClient) -> list[RawArticle]:
    """
    抓取并解析单个 RSS 源。
    返回 RawArticle 列表。
    """
    name = source["name"]
    url = source["url"]
    lang = source.get("lang", "en")

    logger.info("📡 正在抓取: %s (%s)", name, url)

    xml_data = await fetch_feed(url, session)
    if not xml_data:
        return []

    feed = feedparser.parse(xml_data)
    entries = feed.get("entries", [])

    if not entries:
        logger.info("📭 %s: 无新条目", name)

    articles = []
    for entry in entries:
        article = parse_entry(entry, name, url, lang)
        if article:
            articles.append(article)

    logger.info("✅ %s: 解析到 %d 篇文章", name, len(articles))
    return articles


async def fetch_all() -> list[RawArticle]:
    """
    主入口：遍历所有 RSS 源，并发抓取。
    返回所有 RawArticle 的扁平列表（已去重 URL）。
    """
    config = get_config()
    sources = config.rss_sources

    logger.info("=" * 60)
    logger.info("📰 开始抓取 %d 个 RSS 源 ...", len(sources))
    logger.info("=" * 60)

    headers = {"User-Agent": USER_AGENT}

    async with AsyncClient(headers=headers, timeout=TIMEOUT) as session:
        tasks = [fetch_and_parse_source(src.dict(), session) for src in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_articles: list[RawArticle] = []
    seen_urls: set[str] = set()
    fail_count = 0

    for i, result in enumerate(results):
        source_name = sources[i].name
        if isinstance(result, Exception):
            logger.error("❌ %s 抓取异常: %s", source_name, result)
            fail_count += 1
            continue
        for article in result:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                all_articles.append(article)

    logger.info("=" * 60)
    logger.info("📊 RSS 抓取完成: 共 %d 篇（%d 个源失败）",
                len(all_articles), fail_count)
    logger.info("=" * 60)

    return all_articles
