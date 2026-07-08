# AI 热点文章自动生成系统

> 一套全自动化的技术文章采集、筛选、生成与发布流水线。  
> 每日 UTC 01:00（北京时间 09:00）自动执行，零人工干预。

---

## 目录

- [1. 系统概述](#1-系统概述)
- [2. 系统架构](#2-系统架构)
- [3. 模块详解](#3-模块详解)
- [4. 数据流设计](#4-数据流设计)
- [5. 技术选型与设计决策](#5-技术选型与设计决策)
- [6. 配置指南](#6-配置指南)
- [7. 部署与运维](#7-部署与运维)
- [8. 监控与日志](#8-监控与日志)
- [9. 故障处理](#9-故障处理)
- [10. 扩展指南](#10-扩展指南)

---

## 1. 系统概述

### 1.1 背景

个人技术知识库需要持续更新高质量技术内容，但纯人工维护存在以下问题：

- **信息获取成本高**：每天需要浏览多个技术博客、新闻站点，筛选有价值信息
- **内容产出耗时**：一篇深度技术文章的撰写需要 1-2 小时
- **覆盖范围有限**：人工难以同时覆盖国内外多个技术源
- **更新频率不稳定**：受个人时间精力影响，难以保证持续更新

### 1.2 目标

- 每日自动产出 1-3 篇高质量技术热点文章
- 覆盖 Java 后端、AI Agent、云原生等关注领域
- 文章质量稳定，包含结构化深度分析
- 全自动运行，无需人工介入

### 1.3 核心指标

| 指标 | 目标值 | 当前实测 |
|------|--------|---------|
| 每日文章数 | 1-3 篇 | 3 篇 |
| RSS 源数量 | ≥10 个 | 12 个 |
| 单次执行耗时 | < 5 分钟 | ~2.5 分钟 |
| 单次 Token 消耗 | < 50,000 | ~30,000 |
| 关键词过滤准确率 | > 90% | 验证中 |

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GitHub Actions                                 │
│                    每天 UTC 01:00 触发 · cron: 0 1 * * *                    │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ 触发
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            news-bot/ 流水线                                  │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │  RSS 抓取 │───▶│ 关键词过滤│───▶│  去重    │───▶│ AI 评分  │───▶│ LLM 生成│ │
│  │ rss_     │    │ article_ │    │ dedupli- │    │ article_ │    │ llm_   │ │
│  │ reader   │    │ filter   │    │ cator    │    │ filter   │    │summary │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘    └────┬───┘ │
│                                                                       │     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                         │     │
│  │ 列表页   │◀───│ Git 提交 │◀───│ 写入磁盘 │◀────────────────────────┘     │
│  │ 自动更新 │    │ git_    │    │ markdown_│                               │
│  │ index_   │    │ commit   │    │ writer   │                               │
│  │ updater  │    └──────────┘    └──────────┘                               │
│  └──────────┘                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Git push master   │
                    └──────────┬──────────┘
                               │ 触发
                               ▼
                    ┌─────────────────────┐
                    │  GitHub Pages 部署   │
                    │   (deploy.yml)       │
                    └─────────────────────┘
```

### 2.2 模块依赖关系

```
                    ┌─────────────┐
                    │  config.yaml │── 全局配置（RSS 源、关键词、LLM 参数）
                    └─────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  config  │ │  models  │ │  logger  │
        │  .py     │ │  article │ │  .py     │
        └──────────┘ └──────────┘ └──────────┘
              │
     ┌────────┼────────┬────────┬────────┬────────┬────────┐
     │        │        │        │        │        │        │
     ▼        ▼        ▼        ▼        ▼        ▼        ▼
  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
  │ rss_ │ │article│ │dedupl│ │ llm_ │ │mark- │ │index_│ │git_  │
  │reader│ │_filter│ │icator│ │summa-│ │down_ │ │upda- │ │commit│
  │.py   │ │.py    │ │.py   │ │ry.py │ │writer│ │ter.py│ │.py   │
  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
     │        │        │        │        │        │        │
     └────────┴────────┴────────┴────────┴────────┴────────┘
                                │
                                ▼
                          ┌──────────┐
                          │  main.py │── 主编排器
                          └──────────┘
```

---

## 3. 模块详解

### 3.1 主编排器 — `main.py`

**职责**：编排整个流水线的执行顺序，处理异常，生成统计报告。

**流程**：

```
main()
  │
  ├── 加载配置 (load_config)
  ├── 初始化日志 (setup_logging)
  ├── 初始化去重器 (Deduplicator)
  │
  ├── [阶段 1] RSS 抓取 (fetch_all)
  │   ├── 并发请求 12 个 RSS 源
  │   └── 返回 List[RawArticle]
  │
  ├── [阶段 2] 关键词过滤 (keyword_filter)
  │   ├── 严格模式：必须匹配至少一个 include 关键词
  │   └── 排除 exclude 关键词
  │
  ├── [阶段 3] 去重 (dedup.filter_new)
  │   └── 基于 URL 判重，跳过已生成文章
  │
  ├── [阶段 4] AI 评分 (ai_score_filter)
  │   ├── 分批处理（每批 30 篇）
  │   ├── 5 维度综合评分
  │   └── 保留 Top N 篇
  │
  ├── [阶段 5] LLM 逐篇生成
  │   └── 每篇文章调用一次 LLM
  │
  ├── [阶段 6] 更新文章列表页
  │   └── scan_articles → update_index_page
  │
  └── [阶段 7] Git 提交（仅本地环境）
```

**CLI 参数**：

| 参数 | 说明 |
|------|------|
| `--dry-run`, `-n` | 预览模式：抓取 + 过滤 + 评分，不生成文件和提交 |
| `--fetch-only`, `-f` | 仅抓取 RSS，不进行后续处理 |
| `--config`, `-c` | 指定配置文件路径 |

### 3.2 RSS 抓取模块 — `rss_reader.py`

**职责**：并发抓取多个 RSS 源，解析为标准化文章数据。

**关键设计**：

- **异步并发**：使用 `httpx.AsyncClient` 并发请求所有源，单个源失败不影响其他源
- **自动重定向**：`follow_redirects=True` 处理 FeedBurner 等重定向服务
- **全文提取**：通过 `BeautifulSoup` 尝试提取文章正文全文（作为 LLM 生成素材）
- **去重**：在 RSS 层对 URL 去重，防止同一文章出现在多个源中
- **编码兼容**：自动处理 UTF-8/GBK 等编码

**数据模型**：

```python
class RawArticle(BaseModel):
    title: str              # 文章标题
    url: str                # 原文链接
    summary: str            # RSS 摘要
    content: str            # 正文全文（可能为空）
    author: Optional[str]   # 作者
    published: Optional[datetime]  # 发布日期
    source: str             # 来源名称（如 "Baeldung"）
    lang: str               # 语言：en / zh
```

### 3.3 文章过滤模块 — `article_filter.py`

**职责**：两阶段过滤，先低成本快筛，再 AI 精准评分。

#### 第一阶段：关键词快筛

- 规则：标题 + 摘要全文匹配
- 必须包含至少一个 `include` 关键词
- 包含任何 `exclude` 关键词则丢弃
- 大小写不敏感
- 零 API 调用，毫秒级完成

#### 第二阶段：AI 语义评分

- 分批处理（每批 30 篇），避免超出上下文窗口
- 5 维度综合评分（每项 0-20 分）：

| 维度 | 权重 | 评估内容 |
|------|------|---------|
| 热度 | 20% | 当前社区关注度 |
| Java 后端相关性 | 25% | 与技术栈的匹配度 |
| AI 相关性 | 20% | 与 AI/LLM 领域关联度 |
| 工程价值 | 20% | 对实际开发的指导意义 |
| 博客适配度 | 15% | 是否适合知识库读者 |

- 评分 >= 60 分的文章保留
- 按评分排序，取 Top N（默认 3 篇）

### 3.4 去重模块 — `deduplicator.py`

**职责**：持久化记录已生成文章，防止重复生成。

**设计**：

- 使用 JSON 文件存储历史记录（`news-bot/data/history.json`），无额外数据库依赖
- 去重依据：文章 URL（唯一键）
- 每次生成后立即写入，保证数据不丢失

**数据格式**：

```json
{
  "version": 1,
  "last_updated": "2026-07-08T10:00:00",
  "articles": [
    {
      "url": "https://example.com/article",
      "title": "文章标题",
      "slug": "article-slug",
      "file_path": "docs/articles/2026/07/2026-07-08-article.md",
      "generated_at": "2026-07-08T10:00:00"
    }
  ]
}
```

### 3.5 LLM 调用模块 — `llm_summary.py`

**职责**：封装 LLM API 调用，加载 Prompt 模板，解析结构化响应。

**关键设计**：

- **多模型支持**：基于 OpenAI SDK，兼容 DeepSeek、GPT、Qwen 等
- **Prompt 模板化**：所有 Prompt 存放在 `prompts/` 目录，修改 Prompt 无需改代码
- **JSON 结构化输出**：要求 LLM 返回 JSON，包含 title、tags、one_sentence、core_content 等字段
- **多策略解析**：
  1. 优先从 ` ```json ` 代码块提取
  2. 回退到全文第一个 `{...}` 结构
  3. 最后 fallback：全文作为核心内容

### 3.6 Markdown 生成模块 — `markdown_writer.py`

**职责**：将 LLM 生成的结构化数据渲染为 VitePress 标准 Markdown 文件。

**输出规范**：

```markdown
---
title: 文章标题
date: "2026-07-08"
tags: [Java, Spring Boot, AI]
category: 技术热点
source: Baeldung
author: 原作者
description: 一句话总结
---

# 文章标题

## 📝 一句话总结

...

---

## 📌 核心内容

...

## 🎯 为什么值得关注

...

## ✨ 技术亮点

...

## 💭 我的思考

...

---

> 📎 原文链接: [原文](https://...)
```

### 3.7 列表页更新模块 — `article_index_updater.py`

**职责**：自动扫描文章目录，更新入口页 `docs/articles/index.md`。

**设计**：

- 维护 `MARKER_START` / `MARKER_END` 标记之间的自动生成区域
- 保留标记外的手动内容（如分类浏览、说明文字等）
- 每次运行全量扫描目录，重新生成完整列表

### 3.8 Git 提交模块 — `git_commit.py`

**职责**：将生成的文件提交到 Git 仓库。

**模式**：

| 环境 | 行为 |
|------|------|
| 本地开发 | 直接执行 `git add → commit → push` |
| GitHub Actions | 由 workflow 步骤处理（使用 GITHUB_TOKEN 认证） |

---

## 4. 数据流设计

### 4.1 核心数据流

```
RSS XML/Atom
     │ feedparser 解析
     ▼
RawArticle (title, url, summary, content, source, published)
     │ keyword_filter
     ▼
RawArticle[] (已过滤，仅保留相关领域)
     │ dedup.filter_new
     ▼
RawArticle[] (无重复，全新文章)
     │ ai_score_filter (分批 30 篇/批 → LLM 评分)
     ▼
ScoredArticle[] (带 score 评分，按分降序，Top N)
     │ summarize_article (逐篇 LLM 生成)
     ▼
GeneratedArticle (title, tags, one_sentence, core_content, ...)
     │ write_article
     ▼
.md 文件 (docs/articles/YYYY/MM/YYYY-MM-DD-slug.md)
     │ update_index_page
     ▼
docs/articles/index.md (自动生成区域)
     │ git push
     ▼
GitHub → Pages 部署
```

### 4.2 异常处理策略

| 环节 | 策略 |
|------|------|
| RSS 抓取失败 | 跳过该源，记录 WARNING，不影响其他源 |
| 文章内容抓取失败 | 仅用 RSS 摘要，不阻塞流程 |
| 关键词过滤后为空 | 流程终止，记录 INFO |
| AI 评分解析失败 | 记录 ERROR，跳过该批次 |
| LLM 生成失败 | 跳过该篇，继续下一篇 |
| JSON 解析失败 | fallback 到全文模式 |
| Index.md 更新失败 | 记录 WARNING，不阻塞 Git 提交 |
| Git push 冲突 | 记录 WARNING（仅在本地环境） |

---

## 5. 技术选型与设计决策

### 5.1 为什么用 JSON 文件去重而不是数据库？

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| SQLite | 查询能力强、支持复杂条件 | 需要额外依赖、跨平台兼容问题 | ❌ 过度设计 |
| **JSON 文件** | **零依赖、可读性强、易调试** | **全量加载、不适合大规模** | **✅ 适合当前场景** |
| CSV | 简单 | 缺少结构、嵌套数据困难 | ❌ 不适合 |

**结论**：每日生成 1-3 篇，历史记录不超过 1000 条，JSON 文件完全胜任。

### 5.2 为什么分批评分而不是逐篇评分？

- 逐篇评分：195 篇 × 1 次 API = 195 次调用，耗时 15 分钟+
- 分批评分（30 篇/批）：195 / 30 = 7 次调用，耗时 50 秒
- 单次批量评分的质量损失可忽略（LLM 能同时评估多篇文章）

### 5.3 为什么使用 OpenAI SDK 而不是直接调用 API？

- 统一接口：切换模型只需改 `base_url` 和 `model` 名称
- 内置重试机制（需自行配置）
- 内置 Token 计数
- 社区生态丰富

### 5.4 为什么 Prompt 单独放 `prompts/` 目录？

- 将 Prompt 视为一等配置，与代码解耦
- 非技术人员也可修改（纯 Markdown）
- 方便版本对比和管理

---

## 6. 配置指南

### 6.1 配置文件结构

**`config.yaml`** 是所有配置的中心，按功能域划分：

```yaml
llm:
  api_key_env: DEEPSEEK_API_KEY     # 环境变量名（非值）
  base_url: https://api.deepseek.com/v1
  model: deepseek-chat
  temperature: 0.7
  max_tokens: 4096

rss_sources:                         # RSS 源列表
  - name: Baeldung
    url: https://www.baeldung.com/feed
    lang: en

keywords:
  include: [Java, Spring, AI, ...]   # 关注关键词
  exclude: [娱乐, 游戏, ...]         # 排除关键词

output:
  base_dir: docs/articles            # 输出目录
  max_articles_per_day: 3            # 每日最多篇数
```

### 6.2 切换 LLM 模型

```yaml
# OpenAI
llm:
  api_key_env: OPENAI_API_KEY
  base_url: https://api.openai.com/v1
  model: gpt-4o

# DeepSeek（当前默认）
llm:
  api_key_env: DEEPSEEK_API_KEY
  base_url: https://api.deepseek.com/v1
  model: deepseek-chat

# 阿里 Qwen
llm:
  api_key_env: QWEN_API_KEY
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
  model: qwen-plus
```

### 6.3 新增 RSS 源

在 `config.yaml` 的 `rss_sources` 中添加条目即可：

```yaml
rss_sources:
  - name: 自定义源
    url: https://example.com/feed.xml
    type: rss
    lang: zh
```

---

## 7. 部署与运维

### 7.1 GitHub Actions 工作流

**`.github/workflows/news.yml`**

```yaml
name: AI 热点文章自动生成

on:
  schedule:
    - cron: '0 1 * * *'          # 每天 UTC 01:00
  workflow_dispatch:               # 支持手动触发
    inputs:
      dry_run:
        type: boolean
        default: false

jobs:
  generate-articles:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r news-bot/requirements.txt
      - run: python news-bot/main.py
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
      - run: git add docs/articles/ news-bot/data/history.json
      - run: git commit -m "🤖 自动更新热点技术文章"
      - run: git push
```

### 7.2 环境要求

| 环境 | 要求 |
|------|------|
| Python | 3.12+ |
| VitePress | 1.6.4+ |
| API Key | DeepSeek / OpenAI / Qwen 等兼容 API |
| 磁盘 | 生成文章所需空间 < 10 MB/月 |
| 网络 | 需访问 RSS 源和 LLM API |

### 7.3 GitHub Secrets 配置

| Secret Name | 说明 | 必填 |
|-------------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | ✅ |

---

## 8. 监控与日志

### 8.1 执行日志

日志输出到控制台和文件 `news-bot/data/run.log`，格式：

```
2026-07-08 10:00:01 | INFO     | rss_reader | 开始抓取 12 个 RSS 源 ...
2026-07-08 10:00:05 | INFO     | rss_reader | RSS 抓取完成: 共 947 篇
2026-07-08 10:00:05 | INFO     | filter    | 关键词过滤: 947 -> 195 篇
2026-07-08 10:00:05 | INFO     | dedup     | 全部 195 篇均为新文章
2026-07-08 10:01:03 | INFO     | filter    | AI 评分完成: Top 3 篇
2026-07-08 10:02:30 | INFO     | writer    | 已生成: xxx.md
2026-07-08 10:02:35 | INFO     | main      | 
2026-07-08 10:02:35 | INFO     | main      | ======== 执行报告 ========
2026-07-08 10:02:35 | INFO     | main      |   共 947 篇 → 生成 3 篇
2026-07-08 10:02:35 | INFO     | main      |   Token: 30,000
2026-07-08 10:02:35 | INFO     | main      |   耗时: 2分35秒
```

### 8.2 GitHub Actions 监控

- 在 GitHub Actions 页面查看每次运行的状态和日志
- 失败的运行会发送邮件通知
- 支持手动重新运行（`workflow_dispatch`）

### 8.3 执行报告指标

每次运行输出以下指标：

| 指标 | 说明 |
|------|------|
| RSS 抓取数 | 所有源解析到的文章总数 |
| 关键词过滤后 | 通过关键词快筛的文章数 |
| 去重后 | 去除重复后的文章数 |
| AI 评分后 | AI 评分保留的文章数 |
| 最终生成 | 实际生成的文章数 |
| Token 消耗 | prompt + completion tokens |
| 总耗时 | 流水线执行时间 |

---

## 9. 故障处理

### 9.1 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| RSS 源返回 403 | 源站反爬机制 | 更换 User-Agent 或 RSS 地址 |
| RSS 源返回 404 | 地址已变更 | 查找最新 RSS 地址更新 config.yaml |
| LLM API 超时 | 网络波动或 API 限流 | 重试执行；检查 API Key 余额 |
| LLM 评分返回为空 | Prompt 格式问题 | 检查 DeepSeek / 模型是否支持 JSON 输出 |
| JSON 解析失败 | LLM 返回格式不符合预期 | 查看 run.log 中的原始响应，调优 Prompt |
| Git push 失败 | 远程有新的提交 | `git pull --rebase` 后重试 |

### 9.2 快速排查步骤

```bash
# 1. 查看运行日志
cat news-bot/data/run.log

# 2. 检查 LLM API 是否正常
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hello"}]}'

# 3. 查看历史记录
cat news-bot/data/history.json

# 4. 本地预览模式（不生成文件）
cd news-bot && python main.py --dry-run
```

### 9.3 回滚方案

如果生成的文章有问题：

```bash
# 1. 还原被修改的文件
git checkout HEAD -- docs/articles/
git checkout HEAD -- news-bot/data/history.json

# 2. 或者回退到指定 commit
git revert HEAD
```

---

## 10. 扩展指南

### 10.1 新增新闻源

1. 在 `config.yaml` 的 `rss_sources` 中添加条目
2. 确保 URL 可访问（RSS 2.0 或 Atom 格式）
3. （可选）在 `keywords.include` 中添加领域关键词

### 10.2 新增筛选关键词

```yaml
keywords:
  include:
    - Rust              # 新增关注领域
    - WebAssembly
```

### 10.3 调整 LLM 模型

```yaml
llm:
  model: deepseek-chat  # 改为 deepseek-reasoner 启用推理能力
  temperature: 0.7      # 降低到 0.3 提高确定性
```

### 10.4 自定义 Prompt

编辑 `news-bot/prompts/summary.md`：

- 修改文章结构
- 调整输出格式要求
- 添加领域特定的知识约束

### 10.5 添加新的数据源类型（非 RSS）

当前 `rss_reader.py` 只支持 RSS/Atom。如需添加新的数据源类型（如 API 接口、网页爬虫）：

1. 在 `models/article.py` 中定义对应的数据源配置
2. 新增 `xxx_reader.py` 实现抓取逻辑
3. 在 `main.py` 的 `run_pipeline` 中集成

---

## 附录

### A. 文件清单

```
news-bot/
├── main.py                    # 主编排器
├── config.py                  # 配置加载
├── config.yaml                # 全局配置
├── rss_reader.py              # RSS 抓取
├── article_filter.py          # 关键词 + AI 评分
├── deduplicator.py            # 去重管理
├── llm_summary.py             # LLM 调用
├── markdown_writer.py         # Markdown 生成
├── article_index_updater.py   # 列表页更新
├── git_commit.py              # Git 提交
├── logger.py                  # 日志系统
├── __init__.py
├── requirements.txt           # Python 依赖
├── models/
│   ├── __init__.py
│   └── article.py             # 数据模型
├── prompts/
│   ├── filter.md              # AI 筛选 Prompt
│   ├── score.md               # 热点评分 Prompt
│   └── summary.md             # 文章生成 Prompt
└── data/
    └── history.json           # 历史记录
```

### B. 依赖清单

| 包 | 版本 | 用途 |
|---|------|------|
| feedparser | >=6.0.10 | RSS/Atom 解析 |
| httpx | >=0.27.0 | 异步 HTTP |
| beautifulsoup4 | >=4.12.0 | HTML 正文提取 |
| openai | >=1.30.0 | LLM API SDK |
| pyyaml | >=6.0 | YAML 配置解析 |
| pydantic | >=2.0 | 数据模型 |
| lxml | >=5.1.0 | HTML/XML 解析 |
| python-dateutil | >=2.8.0 | 日期解析 |

---

> **维护者**: ZengChuan  
> **最后更新**: 2026-07-08  
> **相关链接**: [README](../../README.md) · [知识库首页](https://zengchuanzc.github.io/knowledge-base/)  
> **参考项目**: [VitePress](https://vitepress.dev/) · [DeepSeek API](https://platform.deepseek.com/)
