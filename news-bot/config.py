"""
配置加载器。

从 config.yaml 读取配置，通过 Pydantic 做类型校验，
提供全局唯一的 Config 对象。
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


# ── 子配置模型 ────────────────────────────────────────────────────────────────

class LLMConfig(BaseModel):
    api_key_env: str = "DEEPSEEK_API_KEY"
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 4096

    @property
    def api_key(self) -> str:
        key = os.environ.get(self.api_key_env)
        if not key:
            raise ValueError(
                f"环境变量 {self.api_key_env} 未设置！"
                f"请设置后再运行。"
            )
        return key


class RSSSourceConfig(BaseModel):
    name: str
    url: str
    type: str = "rss"
    lang: str = "en"


class KeywordsConfig(BaseModel):
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)


class OutputConfig(BaseModel):
    base_dir: str = "docs/articles"
    max_articles_per_day: int = 3


class DedupConfig(BaseModel):
    history_file: str = "news-bot/data/history.json"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file: Optional[str] = "news-bot/data/run.log"


# ── 根配置 ────────────────────────────────────────────────────────────────────

class Config(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    rss_sources: list[RSSSourceConfig] = Field(default_factory=list)
    keywords: KeywordsConfig = Field(default_factory=KeywordsConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    dedup: DedupConfig = Field(default_factory=DedupConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


# ── 全局单例 ──────────────────────────────────────────────────────────────────

_config: Optional[Config] = None


def load_config(config_path: Optional[str] = None) -> Config:
    """
    加载 YAML 配置文件，返回全局唯一的 Config 对象。
    多次调用返回同一实例（单例模式）。
    """
    global _config
    if _config is not None:
        return _config

    if config_path is None:
        # 默认查找项目根目录下的 config.yaml
        script_dir = Path(__file__).parent
        config_path = str(script_dir / "config.yaml")

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    _config = Config(**raw)
    return _config


def get_config() -> Config:
    """获取已加载的配置（必须在调用 load_config 之后使用）。"""
    if _config is None:
        return load_config()
    return _config
