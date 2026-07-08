"""
新闻文章数据模型层。

使用 Pydantic 定义全流程的数据结构，确保模块间契约明确：
  RawArticle      ──▶  RSS 原始文章
  ScoredArticle   ──▶  经过 LLM 评分排序
  GeneratedArticle ──▶  LLM 生成完毕，准备写 MD 文件
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RawArticle(BaseModel):
    """RSS 抓取的原始文章。"""
    title: str
    url: str
    summary: str = ""
    content: str = ""
    author: Optional[str] = None
    published: Optional[datetime] = None
    source: str = ""                     # 来源名称（如 "Spring Blog"）
    source_url: str = ""                 # 来源 RSS URL
    lang: str = "en"                     # 语言：en / zh

    model_config = {"frozen": False}


class ScoredArticle(RawArticle):
    """经过 AI 评分后的文章。"""
    score: float = 0.0                   # 0-100 综合评分
    score_reason: str = ""               # 评分理由


class GeneratedArticle(BaseModel):
    """LLM 生成完毕，准备写入 Markdown 的完整文章。"""
    # ——— 原始信息 ———
    raw_url: str
    raw_source: str
    raw_published: Optional[datetime] = None

    # ——— AI 生成内容 ———
    title: str
    tags: list[str] = Field(default_factory=list)
    category: str = "技术热点"
    cover: Optional[str] = None

    one_sentence: str = ""               # 一句话总结（≤100字）
    core_content: str = ""               # 核心内容（Markdown列表）
    why_worth: str = ""                  # 为什么值得关注
    tech_highlights: str = ""            # 技术亮点
    my_thoughts: str = ""                # 我的思考（≥300字）

    source_url: str = ""                 # 原文链接
    source_author: Optional[str] = None

    # ——— 文件路径信息 ———
    file_path: str = ""                  # 生成的 .md 相对路径
    slug: str = ""                       # URL slug

    model_config = {"frozen": False}
