#!/usr/bin/env python3
"""
AI 热点技术文章生成系统 — 主入口。

每天自动执行：
  1. 抓取 → 2. 过滤 → 3. 判重 → 4. 评分 → 5. 生成 → 6. 保存 → 7. 提交

用法：
  python main.py                          # 完整流程
  python main.py --fetch-only             # 仅抓取
  python main.py --dry-run                # 抓取+过滤+评分，但不生成文件也不提交
  python main.py --config /path/to.yaml   # 指定配置文件
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Optional

import argparse

# 确保项目根在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from logger import setup_logging, get_logger, token_counter, timer
from rss_reader import fetch_all
from article_filter import time_filter, keyword_filter, ai_score_filter
from deduplicator import Deduplicator
from llm_summary import summarize_article
from markdown_writer import write_article
from git_commit import commit_and_push

logger = get_logger("main")


async def run_pipeline(config_path: Optional[str] = None,
                       dry_run: bool = False,
                       fetch_only: bool = False) -> dict:
    """
    执行完整流程。

    返回统计字典：
      {
        "total": N,           # RSS 解析总数
        "after_keyword": N,   # 关键词过滤后
        "after_dedup": N,     # 去重后
        "scored": N,          # AI 评分后
        "generated": N,       # 最终生成
        "token_report": "...", # Token 消耗
        "elapsed": 123.4,     # 总耗时（秒）
        "files": [...],       # 生成的文件路径
      }
    """
    start_time = time.time()

    # ── 0. 初始化 ──
    load_config(config_path)
    setup_logging()
    dedup = Deduplicator()

    stats = {
        "total": 0,
        "after_time": 0,
        "after_keyword": 0,
        "after_dedup": 0,
        "scored": 0,
        "generated": 0,
        "files": [],
    }

    # ── 1. RSS 抓取 ──
    logger.info("")
    logger.info("=" * 60)
    logger.info("🚀 开始执行 AI 热点文章生成流程")
    logger.info("=" * 60)
    logger.info("")

    with timer("RSS 抓取"):
        all_articles = await fetch_all()

    stats["total"] = len(all_articles)

    if not all_articles:
        logger.warning("📭 RSS 抓取为空，流程结束")
        return stats

    if fetch_only:
        logger.info("--fetch-only 模式，流程结束")
        return stats

    # ── 2. 时间窗口过滤（仅保留最近7天） ──
    with timer("时间窗口过滤"):
        all_articles = time_filter(all_articles)

    stats["after_time"] = len(all_articles)

    if not all_articles:
        logger.warning("📭 时间窗口过滤后无文章，流程结束")
        return stats

    # ── 3. 关键词过滤 ──
    with timer("关键词过滤"):
        filtered = keyword_filter(all_articles)

    stats["after_keyword"] = len(filtered)

    if not filtered:
        logger.warning("📭 关键词过滤后无文章，流程结束")
        return stats

    # ── 4. 去重 ──
    new_articles = dedup.filter_new(filtered)
    stats["after_dedup"] = len(new_articles)

    if not new_articles:
        logger.warning("📭 所有文章均已生成过，流程结束")
        return stats

    # ── 5. AI 评分 ──
    with timer("AI 筛选评分"):

        async def score_llm(prompt: str) -> str:
            from llm_summary import chat
            system = "你是一个技术文章评分专家。严格按照用户要求的 JSON 格式输出，不要包含其他文字。"
            return await chat(prompt, system_prompt=system)

        scored = await ai_score_filter(new_articles, score_llm)

    stats["scored"] = len(scored)

    if not scored:
        logger.warning("📭 AI 评分后无合格文章，流程结束")
        return stats

    if dry_run:
        logger.info("🏃 --dry-run 模式: 跳过生成和提交")
        for s in scored:
            logger.info("   [%.0f分] %s", s.score, s.title)
        logger.info("Token 消耗: %s", token_counter.report())
        return stats

    # ── 6. LLM 逐篇生成 ──
    generated_files = []
    with timer("文章内容生成"):
        for i, article in enumerate(scored):
            logger.info("")
            logger.info("─" * 50)
            logger.info("[%d/%d] ✍️  正在生成: %s", i + 1, len(scored), article.title)
            logger.info("─" * 50)

            try:
                article_data = {
                    "title": article.title,
                    "url": article.url,
                    "content": article.content or article.summary,
                    "summary": article.summary,
                    "source": article.source,
                    "author": article.author,
                    "lang": article.lang,
                }

                gen_data = await summarize_article(article_data)
                file_path = await write_article(article, gen_data, dedup)
                generated_files.append(str(file_path))
                stats["generated"] += 1

            except Exception as e:
                logger.error("❌ 文章生成失败 [%s]: %s", article.title[:50], e,
                             exc_info=True)
                continue

    stats["files"] = generated_files

    # ── 6. 更新文章列表页 ──
    if generated_files:
        try:
            from article_index_updater import update_index_page
            update_index_page()
        except Exception as e:
            logger.warning("文章列表页更新失败: %s", e)

    # ── 7. Git 提交（仅在生成文件时） ──
    # 在 GitHub Actions 中，git 操作由 workflow 步骤处理（使用 GITHUB_TOKEN）
    # 本地开发时，可以直接调用 git
    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    if generated_files and not in_ci:
        with timer("Git 提交与推送"):
            today = time.strftime("%Y-%m-%d")
            files_to_add = [
                "docs/articles/",
                "news-bot/data/history.json",
            ]
            commit_and_push(
                commit_message=f"🤖 [自动] 更新热点技术文章 ({today})",
                files=files_to_add,
            )
    elif generated_files and in_ci:
        logger.info("⏩ GitHub Actions 环境：由后续 workflow 步骤处理 git 提交")
    else:
        logger.info("📭 本次未生成新文章，跳过 Git 提交")

    # ── 7. 统计报告 ──
    elapsed = time.time() - start_time

    logger.info("")
    logger.info("=" * 60)
    logger.info("📊 本次执行报告")
    logger.info("=" * 60)
    logger.info(f"   RSS 抓取:    {stats['total']:>4d} 篇")
    logger.info(f"   时间过滤后:  {stats['after_time']:>4d} 篇")
    logger.info(f"   关键词过滤:  {stats['after_keyword']:>4d} 篇")
    logger.info(f"   去重后:      {stats['after_dedup']:>4d} 篇")
    logger.info(f"   AI 评分后:   {stats['scored']:>4d} 篇")
    logger.info(f"   最终生成:    {stats['generated']:>4d} 篇")
    logger.info(f"   {token_counter.report()}")
    logger.info(f"   总耗时:      {elapsed:.1f} 秒")
    logger.info(f"   生成文件:    {len(generated_files)} 个")
    for f in generated_files:
        logger.info(f"     - {f}")
    logger.info("=" * 60)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="AI 热点技术文章生成系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                          # 完整流程
  python main.py --dry-run                # 仅预览
  python main.py --fetch-only             # 仅抓取 RSS
  python main.py --config custom.yaml     # 指定配置
        """,
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help="配置文件路径（默认: config.yaml）",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="预览模式：抓取+过滤+评分，但不生成文件也不提交",
    )
    parser.add_argument(
        "--fetch-only", "-f",
        action="store_true",
        help="仅抓取 RSS，不进行后续处理",
    )

    args = parser.parse_args()

    try:
        if args.dry_run:
            logger.info("🏃 预览模式 (--dry-run)")
        if args.fetch_only:
            logger.info("📡 仅抓取模式 (--fetch-only)")

        stats = asyncio.run(run_pipeline(
            config_path=args.config,
            dry_run=args.dry_run,
            fetch_only=args.fetch_only,
        ))
        return 0
    except KeyboardInterrupt:
        logger.info("\n👋 用户中断")
        return 1
    except Exception as e:
        logger.error("❌ 流程异常结束: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
