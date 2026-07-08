"""
Markdown 文章生成器。

职责：
  1. 根据 GeneratedArticle 生成符合 VitePress 规范的 .md 文件
  2. 自动计算 slug 和文件路径
  3. 写入 docs/articles/yyyy/MM/ 目录
  4. 更新去重记录
"""

import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import get_config
from logger import get_logger
from models.article import GeneratedArticle, RawArticle
from deduplicator import Deduplicator, DedupRecord

logger = get_logger("writer")


def slugify(text: str) -> str:
    """
    将文本转为 URL-friendly 的 slug。

    示例：
      "Spring Boot 3.4 发布" → "spring-boot-3-4-fa-bu"
      "DeepSeek-R1 技术解读" → "deepseek-r1-ji-shu-jie-du"
    """
    # 转小写
    text = text.lower().strip()
    # Unicode 规范化（CJK 字符会保留）
    text = unicodedata.normalize("NFKC", text)
    # 替换空格和特殊字符为连字符
    text = re.sub(r"[^a-z0-9一-鿿＀-￯-]", "-", text)
    # 合并多个连字符
    text = re.sub(r"-+", "-", text)
    # 去除首尾连字符
    text = text.strip("-")
    # 截断（中文 + ASCII 混排，50 个字符够用）
    if len(text) > 80:
        text = text[:80].rstrip("-")
    return text


def build_frontmatter(article: GeneratedArticle) -> str:
    """构建 VitePress FrontMatter。"""
    tags_str = ", ".join(article.tags) if article.tags else "技术热点"

    # 格式化日期
    if article.raw_published:
        date_str = article.raw_published.strftime("%Y-%m-%d")
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "---",
        f"title: {article.title}",
        f'date: "{date_str}"',
        f"tags: [{tags_str}]",
        f"category: {article.category}",
        f"source: {article.raw_source}",
    ]
    if article.one_sentence:
        lines.append(f"description: {article.one_sentence}")
    if article.cover:
        lines.append(f"cover: {article.cover}")
    if article.source_author:
        lines.append(f"author: {article.source_author}")
    lines.append("---")
    lines.append("")  # FrontMatter 后空行

    return "\n".join(lines)


def build_body(article: GeneratedArticle) -> str:
    """构建文章正文字段。"""
    parts = ["", f"# {article.title}", ""]

    # 一句话总结
    parts.append("## 📝 一句话总结")
    parts.append("")
    parts.append(article.one_sentence or "（暂无）")
    parts.append("")

    # 分割线
    parts.append("---")
    parts.append("")

    # 核心内容
    if article.core_content:
        parts.append("## 📌 核心内容")
        parts.append("")
        parts.append(article.core_content)
        parts.append("")

    # 为什么值得关注
    if article.why_worth:
        parts.append("## 🎯 为什么值得关注")
        parts.append("")
        parts.append(article.why_worth)
        parts.append("")

    # 技术亮点
    if article.tech_highlights:
        parts.append("## ✨ 技术亮点")
        parts.append("")
        parts.append(article.tech_highlights)
        parts.append("")

    # 我的思考
    if article.my_thoughts:
        parts.append("## 💭 我的思考")
        parts.append("")
        parts.append(article.my_thoughts)
        parts.append("")

    # 原文链接
    parts.append("---")
    parts.append("")
    parts.append(f"> 📎 **原文链接**: [{article.source_url}]({article.source_url})")
    parts.append("")

    # 元信息
    parts.append(f"> 📅 **文章日期**: {datetime.now().strftime('%Y-%m-%d')}")
    parts.append(f"> 🏷️ **标签**: {', '.join(article.tags) if article.tags else '技术热点'}")
    parts.append(f"> 📂 **分类**: {article.category}")
    parts.append("")

    return "\n".join(parts)


def generate(article: GeneratedArticle) -> str:
    """生成完整的 .md 文件内容。"""
    return build_frontmatter(article) + build_body(article)


def determine_file_path(slug: str,
                        published: Optional[datetime] = None) -> tuple[Path, str]:
    """
    确定文件保存路径。

    路径格式: docs/articles/YYYY/MM/YYYY-MM-DD-slug.md

    返回：
      (相对路径, 路径分段)
    """
    cfg = get_config().output
    base = Path(cfg.base_dir)

    dt = published or datetime.now()
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    date_prefix = dt.strftime("%Y-%m-%d")
    filename = f"{date_prefix}-{slug}.md"

    rel_path = Path(str(base)) / year / month / filename
    return rel_path, f"{year}/{month}/{filename}"


async def write_article(raw: RawArticle,
                        generated_data: dict,
                        dedup: Deduplicator) -> Path:
    """
    写入单篇文章。

    流程：
      1. 确定 slug 和文件路径
      2. 构建文章对象
      3. 生成 Markdown
      4. 写入文件
      5. 更新去重记录

    返回：
      生成的 .md 文件绝对路径
    """
    # 确定 slug
    slug = slugify(generated_data.get("title", raw.title))

    # 确定文件路径（相对于项目根）
    published = raw.published or datetime.now()
    rel_path, path_segment = determine_file_path(slug, published)

    # 项目根 = news-bot 的上级目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    abs_path = (project_root / rel_path).resolve()

    # 创建目录
    abs_path.parent.mkdir(parents=True, exist_ok=True)

    # 构建 GeneratedArticle
    article = GeneratedArticle(
        raw_url=raw.url,
        raw_source=raw.source,
        raw_published=raw.published,
        title=generated_data.get("title", raw.title),
        tags=generated_data.get("tags", []),
        category=generated_data.get("category", "技术热点"),
        cover=generated_data.get("cover"),
        one_sentence=generated_data.get("one_sentence", ""),
        core_content=generated_data.get("core_content", ""),
        why_worth=generated_data.get("why_worth", ""),
        tech_highlights=generated_data.get("tech_highlights", ""),
        my_thoughts=generated_data.get("my_thoughts", ""),
        source_url=raw.url,
        source_author=raw.author,
        file_path=str(rel_path),
        slug=slug,
    )

    # 生成 Markdown 并写入
    content = generate(article)
    abs_path.write_text(content, encoding="utf-8")
    logger.info("📄 已生成文章: %s", abs_path)

    # 记录去重
    record = DedupRecord(
        url=raw.url,
        title=article.title,
        slug=slug,
        file_path=str(rel_path),
    )
    dedup.add_record(record)

    return abs_path


def get_monthly_index_page(year: str, month: str) -> str:
    """
    生成月度索引页 Markdown。

    例如 docs/articles/2026/07/index.md
    用于 VitePress 的目录导航。
    """
    lines = [
        "---",
        "title: 热点技术文章",
        f"date: {year}-{month}-01",
        "---",
        "",
        f"# 📰 {year}年{month}月 热点技术文章",
        "",
        "本月收录的热点技术文章：",
        "",
    ]
    return "\n".join(lines)
