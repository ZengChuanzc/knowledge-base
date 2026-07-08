"""
结构化日志模块。

提供统一的日志输出，支持控制台 + 文件双写，
以及 Token 消耗、耗时等统计辅助。

兼容 Windows GBK 终端（自动替换无法编码的字符）。
"""

import logging
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from config import get_config


class SafeStreamHandler(logging.StreamHandler):
    """
    安全的控制台输出 Handler。
    自动替换当前编码不支持的字符，避免 UnicodeEncodeError。
    """

    def __init__(self, stream=None):
        super().__init__(stream)
        self._encoding = getattr(stream, "encoding", None) or "utf-8"

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            stream.flush()
        except UnicodeEncodeError:
            # 替换不可编码字符为 ASCII 近似
            msg = self.format(record)
            emoji_map = {
                "✅": "[OK]", "❌": "[ERR]", "⚠️": "[WARN]",
                "📡": "[RSS]", "📰": "[NEWS]", "📊": "[STATS]",
                "📭": "[EMPTY]", "📄": "[FILE]", "📖": "[HIST]",
                "💾": "[SAVE]", "🔄": "[SYNC]", "🚀": "[PUSH]",
                "⏱️": "[TIME]", "⭐": "[STAR]", "🔍": "[SEARCH]",
                "🤖": "[AI]", "📝": "[NOTE]", "🎯": "[TARGET]",
                "✨": "[NEW]", "💭": "[THINK]", "📌": "[PIN]",
                "📂": "[DIR]", "🏃": "[DRY]", "🔧": "[CFG]",
                "📦": "[PKG]", "⚙️": "[GEAR]", "🌐": "[WEB]",
                "🛠️": "[TOOL]", "📈": "[CHART]", "⏩": "[SKIP]",
                "🔌": "[PLUG]", "🔒": "[LOCK]", "🔓": "[UNLOCK]",
                "📉": "[DOWN]", "📋": "[LIST]", "📎": "[LINK]",
                "🔄": "[SYNC]", "♻️": "[RECYCLE]",
                "─": "-", "━": "=", "│": "|", "═": "=",
                "「": "[", "」": "]", "『": "[", "』": "]",
            }
            for emoji, replacement in emoji_map.items():
                msg = msg.replace(emoji, replacement)
            try:
                stream.write(msg + self.terminator)
                stream.flush()
            except UnicodeEncodeError:
                # 最终 fallback：ASCII-only
                safe = msg.encode(self._encoding, errors="replace").decode(
                    self._encoding, errors="replace"
                )
                stream.write(safe + self.terminator)
                stream.flush()
        except Exception:
            self.handleError(record)


def setup_logging(log_level: Optional[str] = None,
                  log_file: Optional[str] = None) -> None:
    """
    初始化日志配置。
    支持同时输出到控制台和文件。
    使用 ROOT logger，确保所有模块的日志统一输出。
    """
    cfg = get_config().logging
    level = (log_level or cfg.level).upper()
    fmt = logging.Formatter(cfg.format, datefmt=cfg.date_format)

    # 使用 ROOT logger（所有子 logger 自动继承）
    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))

    # 清除已有 handler
    root.handlers.clear()

    # ── 控制台 Handler（安全版本，兼容 GBK） ──
    console = SafeStreamHandler(sys.stdout)
    console.setFormatter(fmt)
    root.addHandler(console)

    # ── 文件 Handler（UTF-8 编码） ──
    file_path = log_file or cfg.file
    if file_path:
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(p), encoding="utf-8")
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)

    # 防止日志重复传播
    root.info("[OK] 日志初始化完成，级别: %s", level)


def get_logger(name: str = "newsbot") -> logging.Logger:
    """获取命名 Logger（自动继承 ROOT logger 的 handlers）。"""
    return logging.getLogger(name)


# ── Token 计数器 ──────────────────────────────────────────────────────────────

class TokenCounter:
    """简单的 Token 消耗累计器。"""

    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def add(self, prompt: int = 0, completion: int = 0) -> None:
        self.prompt_tokens += prompt
        self.completion_tokens += completion

    @property
    def total(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def report(self) -> str:
        return (
            f"Token 消耗: up {self.prompt_tokens:,} prompt, "
            f"down {self.completion_tokens:,} completion, "
            f"总计 {self.total:,} tokens"
        )


# 全局 Token 计数器
token_counter = TokenCounter()


# ── 计时器上下文 ──────────────────────────────────────────────────────────────

@contextmanager
def timer(label: str = "耗时"):
    """计时上下文管理器，自动记录耗时。"""
    logger = get_logger()
    start = time.time()
    yield
    elapsed = time.time() - start
    logger.info("[TIME] %s: %.1f 秒", label, elapsed)
