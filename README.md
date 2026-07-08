# 📚 Knowledge Base

> **Java · AI Agent · Machine Learning · 个人技术知识库**

[![GitHub Pages](https://img.shields.io/badge/deployed-GitHub%20Pages-blue)](https://zengchuanzc.github.io/knowledge-base/)
[![VitePress](https://img.shields.io/badge/built%20with-VitePress-4fc08d)](https://vitepress.dev/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![AI Generated](https://img.shields.io/badge/dynamic%20news-AI%20auto--generated-orange)](https://github.com/ZengChuanzc/knowledge-base/actions/workflows/news.yml)

基于 **VitePress** 构建的个人技术知识库，涵盖 Java 后端、AI Agent、机器学习等方向的学习笔记与知识沉淀。  
集成 **AI 热点文章自动生成系统**，每天自动抓取、筛选、总结技术文章并发布。

🌐 **在线访问**: [https://zengchuanzc.github.io/knowledge-base/](https://zengchuanzc.github.io/knowledge-base/)

---

## 📂 内容导航

| 栏目 | 说明 |
|------|------|
| ☕ [Java 体系](https://zengchuanzc.github.io/knowledge-base/java/) | JDK 版本特性、JVM、并发编程、Spring 生态 |
| 🤖 [AI Agent](https://zengchuanzc.github.io/knowledge-base/ai-agent/) | LLM 基础、RAG、Spring AI、MCP 协议 |
| 📊 [机器学习](https://zengchuanzc.github.io/knowledge-base/ml/) | 机器学习入门笔记 |
| 🏗️ [项目实践](https://zengchuanzc.github.io/knowledge-base/projects/) | 企业级项目案例 |
| 📰 [热点文章](https://zengchuanzc.github.io/knowledge-base/articles/) | **AI 自动生成** 每日技术热点 |
| 🗺️ [学习路线](https://zengchuanzc.github.io/knowledge-base/roadmap/) | Java 后端 & AI 学习路径 |
| 📌 [技术导航](https://zengchuanzc.github.io/knowledge-base/navigation/) | 工具与资源索引 |

---

## 🤖 AI 热点文章自动生成系统

这是本项目的核心亮点 — 一套完全自动化的技术文章采集、筛选、生成与发布流水线。

### 系统架构

```
RSS 新闻源（12 个）
       │
       ▼
┌─────────────────────────────────────────────┐
│              news-bot/ 流水线                 │
│                                             │
│  ① RSS 并发抓取  │  feedparser + httpx       │
│  ② 关键词快筛     │  40+ 技术关键词严格匹配    │
│  ③ 去重          │  history.json 持久化       │
│  ④ AI 评分       │  DeepSeek 语义评分选 Top 3 │
│  ⑤ AI 生成       │  结构化文章生成             │
│  ⑥ 写入磁盘      │  Markdown + FrontMatter   │
│  ⑦ 更新列表页    │  自动追加文章入口           │
│  ⑧ Git 提交      │  自动 push → 触发部署      │
└─────────────────────────────────────────────┘
       │
       ▼
    GitHub Actions（每天 UTC 01:00 / 北京时间 09:00）
       │
       ▼
    GitHub Pages 自动部署
```

### 工作流程

每天北京时间 **09:00**，系统自动执行：

1. **📡 抓取** — 从 12 个国内外技术博客抓取最新文章
2. **🔍 过滤** — 关键词快筛（947 → 195 篇）+ AI 语义评分（195 → Top 3）
3. **✍️ 生成** — DeepSeek 大模型生成结构化文章（含一句话总结、核心内容、技术亮点、深度思考）
4. **📄 发布** — 自动写入 `docs/articles/` 目录，更新列表页，提交并推送到 GitHub
5. **🚀 部署** — GitHub Actions 自动构建并部署到 Pages

### 支持的 RSS 源

| 来源 | 语言 | 状态 |
|------|------|------|
| Baeldung | EN | ✅ |
| InfoQ | EN | ✅ |
| GitHub Blog | EN | ✅ |
| HuggingFace Blog | EN | ✅ |
| Microsoft Dev Blog | EN | ✅ |
| Netflix TechBlog | EN | ✅ |
| InfoQ 中文 | ZH | ✅ |
| 开源中国 | ZH | ✅ |
| Spring Blog | EN | ⏳ 待修复 |
| Red Hat Developer | EN | ⏳ 待修复 |
| Google AI Blog | EN | ⏳ 待修复 |
| 阿里云云原生 | ZH | ⏳ 待修复 |

> 所有源均通过 `news-bot/config.yaml` 配置化，新增/修复无需修改代码。

### 筛选规则

AI 自动筛选覆盖但不限于以下技术领域：

**后端 & 架构**: Java, Spring Boot, Spring AI, 微服务, 云原生, Kubernetes, Docker, Redis, MySQL, Kafka, RocketMQ  
**AI & LLM**: AI Agent, LLM, RAG, MCP, Prompt Engineering, LangChain4j  
**开发工具**: GitHub Copilot, Cursor, Claude, OpenAI, DeepSeek, Qwen  
**性能 & 设计**: 高并发, 分布式, 性能优化, 系统设计, Virtual Thread, GraalVM

### 文章质量标准

每篇生成的文章包含 7 个结构化部分：

```
📝 一句话总结    → 100 字以内
📌 核心内容      → Markdown 列表
🎯 为什么值得关注 → Java 开发者视角
✨ 技术亮点      → 功能/架构/性能/API 变化
💭 我的思考      → 300+ 字深度分析
📎 原文链接      → 保留来源
```

---

## 🛠️ 技术栈

### 前端 / 静态站点

| 技术 | 用途 |
|------|------|
| [VitePress 1.6.4](https://vitepress.dev/) | Vue 3 + Vite 静态站点框架 |
| Vue 3 | 自定义布局与组件 |
| Canvas | 粒子鼠标追踪动效 |
| HTML / CSS | 响应式布局，毛玻璃导航栏 |

### AI 流水线 (news-bot/)

| 技术 | 用途 |
|------|------|
| Python 3.12+ | 核心开发语言 |
| feedparser | RSS/Atom 解析 |
| httpx | 异步 HTTP 客户端 |
| BeautifulSoup4 | HTML 正文提取 |
| OpenAI SDK | DeepSeek API 调用（OpenAI 兼容接口） |
| Pydantic | 数据模型与配置校验 |

---

## 🚀 本地开发

```bash
# 1. 安装前端依赖
npm install

# 2. 启动 VitePress 开发服务器
npm run dev

# 3. 构建生产版本
npm run build
```

### 运行 AI 流水线

```bash
cd news-bot

# 安装 Python 依赖
pip install -r requirements.txt

# 设置 API Key（DeepSeek / OpenAI 兼容）
export DEEPSEEK_API_KEY="sk-xxxx"

# 预览模式（仅抓取 + 过滤 + 评分，不生成文件）
python main.py --dry-run

# 仅抓取 RSS
python main.py --fetch-only

# 完整流程
python main.py
```

### 项目结构

```
knowledge-base/
├── docs/                          # VitePress 站点目录
│   ├── .vitepress/                # 主题、配置、样式
│   ├── articles/                  # AI 自动生成的文章（按年/月分类）
│   ├── java/                      # Java 体系笔记
│   ├── ai-agent/                  # AI Agent 笔记
│   ├── ml/                        # 机器学习笔记
│   └── ...
│
├── news-bot/                      # AI 自动文章生成系统
│   ├── main.py                    # 主编排器
│   ├── rss_reader.py              # RSS 抓取
│   ├── article_filter.py          # 关键词 + AI 评分过滤
│   ├── llm_summary.py             # DeepSeek API 调用
│   ├── markdown_writer.py         # Markdown 生成
│   ├── article_index_updater.py   # 列表页自动更新
│   ├── deduplicator.py            # 去重
│   ├── git_commit.py              # Git 提交
│   ├── config.py / config.yaml    # 全局配置
│   ├── prompts/                   # LLM Prompt 模板
│   └── models/                    # 数据模型
│
├── .github/workflows/
│   ├── news.yml                   # 每日 09:00 自动执行
│   └── deploy.yml                 # GitHub Pages 部署
│
└── README.md
```

---

## ⚙️ 配置说明

所有配置集中在 `news-bot/config.yaml`：

```yaml
llm:
  model: deepseek-chat              # 可选 gpt-4o / qwen-plus / claude
  base_url: https://api.deepseek.com/v1

rss_sources:                        # 新增源只需在这里添加
  - name: 自定义源
    url: https://example.com/feed
    lang: zh

keywords:
  include: [Java, Spring, AI, ...]  # 关注关键词
  exclude: [娱乐, 游戏, ...]        # 排除关键词

output:
  max_articles_per_day: 3           # 每天最多生成篇数
```

---

## 🤝 贡献

- 📖 **内容建议**: 通过 [Issues](https://github.com/ZengChuanzc/knowledge-base/issues) 提交
- 🔧 **技术改进**: Fork 并提交 PR
- 📡 **RSS 源**: 在 `config.yaml` 中添加即可

---

## 📄 许可

本项目内容仅供学习参考，文章版权归原作者所有。

---

<p align="center">
  🚀 <strong>学无止境 · 行以致远</strong>
</p>
