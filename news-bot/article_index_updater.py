"""
文章列表页自动更新模块。

每次生成新文章后，自动扫描 docs/articles/ 目录，
更新 index.md 中的「最新文章」列表。

原理：在 index.md 中维护两个标记注释之间的区域，
      自动扫描并渲染文章卡片，保留标记外的页面内容。
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import get_config
from logger import get_logger
from models.article import GeneratedArticle

logger = get_logger("index_updater")

# 自动生成区域的标记
MARKER_START = "<!-- AUTO_GENERATED_ARTICLES_START -->"
MARKER_END = "<!-- AUTO_GENERATED_ARTICLES_END -->"

# VitePress 站点 base 路径（与 docs/.vitepress/config.ts 中的 base 一致）
# 用于生成正确的文章 URL
BASE_PATH = "/knowledge-base"


def scan_articles(articles_dir: Path) -> list[dict]:
    """
    扫描 articles 目录，提取所有 .md 文件的元数据（不包含 index.md）。
    返回按日期降序排列的文章列表。
    """
    articles = []
    for md_file in sorted(articles_dir.rglob("*.md")):
        # 跳过 index.md
        if md_file.name == "index.md":
            continue

        content = md_file.read_text(encoding="utf-8")
        meta = parse_frontmatter(content)
        if meta and meta.get("title"):
            # 计算文章 URL（相对于 docs/ 目录）
            # VitePress 生成 xxx.html，所以 URL 需要 .html 后缀
            rel_path = md_file.relative_to(articles_dir.parent)  # 相对于 docs/
            url_path = str(rel_path.with_suffix(".html")).replace("\\", "/")
            url = f"{BASE_PATH}/{url_path}"

            meta["url"] = url
            meta["_file"] = str(md_file)
            articles.append(meta)

    # 按日期降序
    articles.sort(key=lambda a: a.get("date", ""), reverse=True)
    return articles


def parse_frontmatter(content: str) -> Optional[dict]:
    """
    简易 FrontMatter 解析器。
    从 Markdown 中提取 --- 之间的 YAML 字段。
    """
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    yaml_text = match.group(1)
    meta = {}
    for line in yaml_text.split("\n"):
        line = line.strip()
        # 跳过空行和注释
        if not line or line.startswith("#"):
            continue
        # 解析 key: value
        kv_match = re.match(r"^(\w+):\s*(.+)$", line)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip()
            # 处理引号
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            # 处理列表 [a, b, c]
            if value.startswith("[") and value.endswith("]"):
                items = value[1:-1].split(",")
                value = [item.strip().strip("'\"") for item in items if item.strip()]
            meta[key] = value
    return meta


def build_article_card(article: dict) -> str:
    """为单篇文章生成卡片 HTML。"""
    title = article.get("title", "无标题")
    url = article.get("url", "#")
    date = article.get("date", "")
    tags = article.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.strip("[]").split(",") if t.strip()]
    source = article.get("source", "")
    description = article.get("description", "")

    # 格式化日期
    date_display = date
    if date and len(date) >= 10:
        try:
            dt = datetime.strptime(date[:10], "%Y-%m-%d")
            date_display = f"{dt.month}月{dt.day}日"
        except ValueError:
            pass

    tag_html = " ".join(
        f'<span class="article-tag">{tag}</span>'
        for tag in tags[:4]
    )

    return f"""\
<div class="article-item" onclick="location.href='{url}'">
  <span class="article-meta-date">{date_display}</span>
  <span class="article-source">{source}</span>
  <h3><a href="{url}">{title}</a></h3>
  <p class="article-desc">{description or title}</p>
  <div class="article-tags">{tag_html}</div>
</div>"""


def build_auto_section(articles: list[dict], base_url: str = "") -> str:
    """
    构建自动生成区域的完整内容。
    保留手动标记。
    """
    if not articles:
        return f"{MARKER_START}\n\n<p>暂无文章，等待自动生成中...</p>\n\n{MARKER_END}"

    cards = [build_article_card(a) for a in articles]
    cards_html = "\n\n".join(cards)

    return f"""\
{MARKER_START}

<div class="article-list-auto">
{cards_html}
</div>

<style>
.article-list-auto .article-item {{
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 1.1rem 1.25rem;
  margin-bottom: 0.75rem;
  background: var(--vp-c-bg-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}}
.article-list-auto .article-item:hover {{
  border-color: var(--vp-c-brand-1);
  transform: translateY(-1px);
}}
.article-list-auto .article-item h3 {{
  margin: 0.3rem 0 0.4rem;
  font-size: 1rem;
  font-weight: 600;
}}
.article-list-auto .article-item h3 a {{
  color: var(--vp-c-text-1);
  text-decoration: none;
}}
.article-list-auto .article-item:hover h3 a {{
  color: var(--vp-c-brand-1);
}}
.article-meta-date {{
  font-size: 0.82rem;
  color: var(--vp-c-text-3);
  margin-right: 0.5rem;
}}
.article-source {{
  font-size: 0.78rem;
  color: var(--vp-c-text-3);
}}
.article-desc {{
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  margin: 0 0 0.4rem;
  line-height: 1.5;
}}
.article-tags {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}}
.article-tag {{
  font-size: 0.72rem;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
  background: #eef2ff;
  color: #4f46e5;
}}
:root.dark .article-tag {{
  background: #1e1b4b;
  color: #a5b4fc;
}}
</style>

{MARKER_END}"""


def update_index_page(articles_dir: Optional[Path] = None) -> bool:
    """
    更新 docs/articles/index.md 中的自动生成文章区域。

    流程：
      1. 扫描 articles 目录下的所有 .md 文件
      2. 提取 FrontMatter 元数据
      3. 生成卡片 HTML
      4. 插入到 index.md 的标记区域内

    返回：
      True 表示 index.md 有变更，False 表示无变更
    """
    if articles_dir is None:
        cfg = get_config().output
        articles_dir = Path(cfg.base_dir)

    if not articles_dir.exists():
        logger.warning("文章目录不存在: %s", articles_dir)
        return False

    index_path = articles_dir / "index.md"
    if not index_path.exists():
        logger.warning("index.md 不存在: %s", index_path)
        return False

    # 扫描文章
    articles = scan_articles(articles_dir)
    logger.info("扫描到 %d 篇文章，正在更新列表页", len(articles))

    # 生成新区域
    new_section = build_auto_section(articles)

    # 读取当前 index.md
    current = index_path.read_text(encoding="utf-8")

    # 检查是否已有标记区域
    if MARKER_START in current and MARKER_END in current:
        # 替换标记之间的内容
        pattern = re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END)
        updated = re.sub(pattern, new_section, current, flags=re.DOTALL)
    else:
        # 在文件末尾追加（保留手动内容）
        # 但更合理的做法：在第一个 ## 之前或之后插入
        # 简单起见，追加到 --- 之后、第一个二级标题之前
        updated = current + "\n\n## 🔥 最新文章\n\n" + new_section

    if updated == current:
        logger.info("列表页无变更")
        return False

    index_path.write_text(updated, encoding="utf-8")
    logger.info("已更新文章列表页: %s", index_path)
    return True
