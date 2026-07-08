"""
去重模块。

基于 history.json 持久化已生成记录。
核心去重依据：文章 URL（唯一 key）。
辅助：标题相似度。

history.json 结构：
{
  "version": 1,
  "articles": [
    {
      "url": "https://...",
      "title": "...",
      "slug": "...",
      "generated_at": "2026-07-08T10:00:00",
      "file_path": "docs/articles/2026/07/2026-07-08-xxx.md"
    },
    ...
  ]
}
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import get_config
from logger import get_logger
from models.article import RawArticle

logger = get_logger("dedup")


class DedupRecord:
    """单条历史记录。"""
    def __init__(self, url: str, title: str, slug: str,
                 file_path: str, generated_at: Optional[str] = None):
        self.url = url
        self.title = title
        self.slug = slug
        self.file_path = file_path
        self.generated_at = generated_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "slug": self.slug,
            "file_path": self.file_path,
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DedupRecord":
        return cls(
            url=d["url"],
            title=d["title"],
            slug=d["slug"],
            file_path=d["file_path"],
            generated_at=d.get("generated_at"),
        )


class Deduplicator:
    """
    去重管理器。
    负责：
      - 读取/写入 history.json
      - 基于 URL 判重
      - 查询是否已生成
    """

    def __init__(self):
        cfg = get_config().dedup
        self.history_path = Path(cfg.history_file)
        self.records: list[DedupRecord] = []
        self._known_urls: set[str] = set()
        self._load()

    def _load(self) -> None:
        """从磁盘加载历史记录。"""
        if not self.history_path.exists():
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            self._save()  # 创建空文件
            return

        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_list = data.get("articles", [])
            self.records = [DedupRecord.from_dict(r) for r in raw_list]
            self._known_urls = {r.url for r in self.records}
            logger.info("📖 已加载 %d 条历史记录", len(self.records))
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("⚠️  历史记录文件损坏，将重新创建: %s", e)
            self.records = []
            self._known_urls = set()
            self._save()

    def _save(self) -> None:
        """将历史记录写入磁盘。"""
        data = {
            "version": 1,
            "last_updated": datetime.now().isoformat(),
            "articles": [r.to_dict() for r in self.records],
        }
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def is_duplicate(self, article: RawArticle) -> bool:
        """检查文章是否已生成过（基于 URL）。"""
        return article.url in self._known_urls

    def filter_new(self, articles: list[RawArticle]) -> list[RawArticle]:
        """过滤掉已生成过的文章，返回全新列表。"""
        new = [a for a in articles if not self.is_duplicate(a)]
        skipped = len(articles) - len(new)
        if skipped:
            logger.info("🔄 去重跳过 %d 篇已有文章", skipped)
        else:
            logger.info("✅ 全部 %d 篇均为新文章", len(articles))
        return new

    def add_record(self, record: DedupRecord) -> None:
        """添加一条新生成记录并持久化。"""
        if record.url in self._known_urls:
            logger.debug("记录已存在: %s", record.url)
            return
        self.records.append(record)
        self._known_urls.add(record.url)
        self._save()
        logger.info("💾 已记录文章: %s → %s", record.title[:50], record.file_path)

    def add_records(self, records: list[DedupRecord]) -> None:
        """批量添加。"""
        for r in records:
            self.add_record(r)
