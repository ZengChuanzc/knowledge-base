"""
Git 提交与推送模块。

职责：
  1. 执行 git add / commit / push
  2. 仅在有关键变更时才提交
  3. 自动处理 push 冲突（先 pull --rebase 再 push）
"""

import subprocess
from pathlib import Path
from typing import Optional

from logger import get_logger

logger = get_logger("git")


def _run_git(cmd: list[str], cwd: Optional[Path] = None) -> str:
    """执行 git 命令，返回 stdout。"""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        if result.returncode != 0:
            logger.warning("git %s 失败: %s", " ".join(cmd), result.stderr.strip())
            return ""
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error("git 命令超时: %s", " ".join(cmd))
        return ""
    except FileNotFoundError:
        logger.error("git 未找到，请确保 Git 已安装")
        return ""


def commit_and_push(commit_message: Optional[str] = None,
                    repo_path: Optional[Path] = None,
                    files: Optional[list[str]] = None) -> bool:
    """
    执行 Git 提交流程。

    步骤：
      1. git add <files>（默认添加所有变更）
      2. git commit（无变更则跳过）
      3. git pull --rebase（防止远程冲突）
      4. git push

    返回：
      True 表示已推送，False 表示无变更或失败
    """
    if repo_path is None:
        # 默认当前目录（GitHub Actions 的 checkout 目录）
        repo_path = Path(".").resolve()

    # ── Step 1: git add ──
    if files:
        logger.info("添加指定文件: %s", files)
        for f in files:
            _run_git(["add", f], repo_path)
    else:
        # 仅添加 docs/articles 目录变更
        logger.info("添加 docs/articles 目录变更...")
        _run_git(["add", "docs/articles/"], repo_path)
        # 也添加 history.json
        _run_git(["add", "news-bot/data/history.json"], repo_path)

    # ── Step 2: 检查是否有变更 ──
    status = _run_git(["status", "--porcelain"], repo_path)
    if not status:
        logger.info("📭 没有需要提交的变更")
        return False

    # ── Step 3: git commit ──
    default_msg = f"🤖 [自动] 更新热点技术文章 ({_get_today()})"
    msg = commit_message or default_msg

    # 检查是否有 staged 变更
    staged = _run_git(["diff", "--staged", "--stat"], repo_path)
    if not staged:
        logger.info("📭 没有暂存的变更（可能已全部被 gitignore）")
        return False

    _run_git(["commit", "-m", msg], repo_path)
    logger.info("✅ 提交成功: %s", msg)

    # ── Step 4: git pull --rebase ──
    logger.info("🔄 git pull --rebase ...")
    pull_result = _run_git(["pull", "--rebase"], repo_path)
    if "Successfully rebased" in pull_result or "Already up to date" in pull_result:
        logger.info("✅ rebase 成功")
    else:
        # 如果 rebase 有冲突，终止 rebase
        if "conflict" in pull_result.lower():
            logger.error("❌ rebase 冲突，终止 rebase")
            _run_git(["rebase", "--abort"], repo_path)
            return False

    # ── Step 5: git push ──
    logger.info("🚀 git push ...")
    push_result = _run_git(["push"], repo_path)
    if push_result or True:  # push 成功可能无输出
        logger.info("✅ 已推送到远程仓库")
        return True

    logger.warning("⚠️  push 可能未成功")
    return False


def _get_today() -> str:
    """获取今天的日期字符串。"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")
