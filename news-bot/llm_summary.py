"""
LLM 调用封装模块。

基于 OpenAI SDK，支持任意 OpenAI 兼容 API（DeepSeek、Qwen 等）。
从 config.yaml 读取 base_url 和 model，从环境变量读取 API Key。

所有 Prompt 模板存放在 prompts/ 目录，通过 read_prompt() 加载。
"""

from pathlib import Path
from typing import Optional

from openai import AsyncOpenAI

from config import get_config
from logger import get_logger, token_counter

logger = get_logger("llm")


# ── Prompt 加载 ───────────────────────────────────────────────────────────────

_prompt_cache: dict[str, str] = {}


def read_prompt(name: str, **kwargs) -> str:
    """
    从 prompts/ 目录读取 Prompt 模板。

    Prompt 文件使用 {{placeholder}} 作为占位符，
    通过 kwargs 替换。

    用法:
        prompt = read_prompt("summary.md", title="xxx", content="...")
    """
    if name in _prompt_cache:
        template = _prompt_cache[name]
    else:
        script_dir = Path(__file__).parent
        prompt_path = script_dir / "prompts" / name
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt 模板不存在: {prompt_path}")
        template = prompt_path.read_text(encoding="utf-8")
        _prompt_cache[name] = template

    if kwargs:
        # 简单替换 {{key}} 为 value（无需额外依赖）
        result = template
        for key, value in kwargs.items():
            result = result.replace("{{" + key + "}}", str(value))
        return result

    return template


# ── LLM 客户端 ────────────────────────────────────────────────────────────────

_client: Optional[AsyncOpenAI] = None


def get_client() -> AsyncOpenAI:
    """获取 LLM 客户端单例。"""
    global _client
    if _client is not None:
        return _client

    cfg = get_config().llm
    _client = AsyncOpenAI(
        api_key=cfg.api_key,
        base_url=cfg.base_url,
    )
    logger.info("[PLUG] LLM 客户端初始化: model=%s base_url=%s",
                cfg.model, cfg.base_url)
    return _client


async def chat(prompt: str,
               system_prompt: Optional[str] = None,
               temperature: Optional[float] = None,
               max_tokens: Optional[int] = None) -> str:
    """
    调用 LLM 聊天补全接口。

    参数：
      prompt: 用户提示词（即 prompt 模板填充后的内容）
      system_prompt: 系统提示词（可选）
      temperature: 温度（默认从配置读取）
      max_tokens: 最大 Token 数（默认从配置读取）

    返回：
      LLM 响应文本
    """
    cfg = get_config().llm
    client = get_client()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    temp = temperature if temperature is not None else cfg.temperature
    max_tk = max_tokens if max_tokens is not None else cfg.max_tokens

    try:
        response = await client.chat.completions.create(
            model=cfg.model,
            messages=messages,
            temperature=temp,
            max_tokens=max_tk,
        )

        # 记录 Token 消耗
        usage = response.usage
        if usage:
            token_counter.add(
                prompt=usage.prompt_tokens or 0,
                completion=usage.completion_tokens or 0,
            )
            logger.debug("Token: ↑%d / ↓%d / 总计%d",
                         usage.prompt_tokens, usage.completion_tokens,
                         usage.total_tokens)

        content = response.choices[0].message.content or ""
        return content

    except Exception as e:
        logger.error("❌ LLM 调用失败: %s", e, exc_info=True)
        raise


async def summarize_article(article_data: dict) -> dict:
    """
    根据文章信息，调用 LLM 生成完整文章内容。

    参数：
      article_data: 包含 title, content, summary, source 等信息的字典

    返回：
      包含生成内容的字典（与 GeneratedArticle 字段对应）
    """
    prompt = read_prompt(
        "summary.md",
        title=article_data.get("title", ""),
        content=article_data.get("content", "") or article_data.get("summary", ""),
        source=article_data.get("source", ""),
    )

    system = (
        "你是一位资深的 Java 全栈架构师和技术博主，"
        "擅长用中文撰写高质量的技术文章。"
        "你的文章深入浅出，既有技术深度又贴近实战。"
    )

    response = await chat(prompt, system_prompt=system)

    return parse_generated_content(response, article_data)


def parse_generated_content(response: str, article_data: dict) -> dict:
    """
    解析 LLM 返回的文章内容。
    支持三种格式：
      1. ```json ... ``` 代码块包裹
      2. 纯 JSON（无代码块）
      3. 自然语言 Markdown（fallback）
    """
    import json
    import re

    # 尝试多种策略提取 JSON
    json_str = None

    # 策略1：从 ```json ... ``` 代码块中提取
    fenced = re.search(
        r"```(?:json)?\s*([\s\S]*?)\s*```", response
    )
    if fenced:
        candidate = fenced.group(1).strip()
        if candidate.startswith("{"):
            json_str = candidate

    # 策略2：直接找第一个 { 和最后一个 }
    if json_str is None:
        start = response.find("{")
        end = response.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = response[start:end + 1]

    # 解析 JSON
    if json_str:
        # 预处理：修复 JSON 中的常见问题
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # 尝试修复：处理字符串中未转义的控制字符
            try:
                # 替换字符串值中的未转义换行符
                cleaned = re.sub(
                    r'"(?:\\.|[^"\\])*"',
                    lambda m: m.group(0).replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t"),
                    json_str,
                )
                data = json.loads(cleaned)
            except json.JSONDecodeError:
                logger.warning("JSON 解析失败，回退到全文模式")
                data = None

        if data and isinstance(data, dict):
            # 保存解析后的 JSON 到日志以便调试
            logger.debug("成功解析结构化 JSON 响应")

            # 后处理：去除内容字段中自带的 Markdown 标题（模板已提供）
            def strip_first_heading(text: str) -> str:
                """去掉内容开头的 # 标题行（由模板统一添加）。"""
                import re as _re
                return _re.sub(r"^#+\s+.*?\n\n?", "", text, count=1).strip()

            return {
                "title": data.get("title", article_data.get("title", "")),
                "tags": data.get("tags", []),
                "category": data.get("category", "技术热点"),
                "cover": data.get("cover"),
                "one_sentence": data.get("one_sentence", ""),
                "core_content": strip_first_heading(
                    data.get("core_content", "") or data.get("核心内容", "")
                ),
                "why_worth": strip_first_heading(
                    data.get("why_worth", "") or data.get("为什么值得关注", "")
                ),
                "tech_highlights": strip_first_heading(
                    data.get("tech_highlights", "") or data.get("技术亮点", "")
                ),
                "my_thoughts": strip_first_heading(
                    data.get("my_thoughts", "") or data.get("我的思考", "")
                ),
                "source_url": article_data.get("url", ""),
                "source_author": article_data.get("author"),
            }

    # Fallback：直接返回全文作为核心内容
    logger.warning("LLM 未返回结构化 JSON，使用全文 fallback")
    return {
        "title": article_data.get("title", ""),
        "tags": [],
        "category": "技术热点",
        "cover": None,
        "one_sentence": "",
        "core_content": response[:3000],
        "why_worth": "",
        "tech_highlights": "",
        "my_thoughts": response[3000:6000] if len(response) > 3000 else response,
        "source_url": article_data.get("url", ""),
        "source_author": article_data.get("author"),
    }
