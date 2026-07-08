<p align="center">
  <img alt="Knowledge Base" src="https://zengchuanzc.github.io/knowledge-base/k-icon.svg" width="64">
</p>

<h1 align="center">ZengChuan · 知识库</h1>

<p align="center">
  <code>Java</code>&nbsp;
  <code>Spring Boot</code>&nbsp;
  <code>Spring Cloud</code>&nbsp;
  <code>AI Agent</code>&nbsp;
  <code>LLM+RAG</code>&nbsp;
  <code>微服务</code>&nbsp;
  <code>Kafka</code>&nbsp;
  <code>Redis</code>
</p>

<p align="center">
  <a href="https://github.com/ZengChuanzc"><img src="https://img.shields.io/badge/GitHub-ZengChuanzc-181717?logo=github&style=flat" alt="GitHub"></a>
  <a href="https://zengchuanzc.github.io/knowledge-base/"><img src="https://img.shields.io/badge/%F0%9F%93%96_%E5%9C%A8%E7%BA%BF%E7%9F%A5%E8%AF%86%E5%BA%93-visit-4fc08d?style=flat" alt="Knowledge Base"></a>
  <a href="https://github.com/ZengChuanzc/knowledge-base/stargazers"><img src="https://img.shields.io/github/stars/ZengChuanzc/knowledge-base?style=flat&logo=github" alt="Stars"></a>
  <a href="https://github.com/ZengChuanzc/knowledge-base/actions/workflows/deploy.yml"><img src="https://img.shields.io/github/actions/workflow/status/ZengChuanzc/knowledge-base/deploy.yml?label=deploy" alt="Build"></a>
  <a href="https://github.com/ZengChuanzc/knowledge-base/actions/workflows/news.yml"><img src="https://img.shields.io/badge/AI_News-daily-orange" alt="AI News"></a>
  <img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python">
</p>

<br>

<p align="center">
  <a href="https://zengchuanzc.github.io/knowledge-base/">
    <img src="https://zengchuanzc.github.io/knowledge-base/docs/public/img/index.png" alt="知识库首页截图" width="720" style="border-radius: 8px; border: 1px solid #e2e8f0;">
  </a>
  <br>
  <sub>⬆ 知识库首页 · Java 后端 · AI Agent · 学习笔记</sub>
</p>

<br>

<p align="center">
  致力于将技术知识系统化的个人知识库，覆盖 <strong>Java 后端</strong>、<strong>AI Agent</strong> 两大主线。<br>
  集成 <strong>AI 自动文章生成系统</strong>，每天追踪前沿技术，自动输出结构化技术解读。
</p>

---

## 🧑‍💻 关于我

4 年 Java 后端开发经验，目前专注于 Spring Boot / Spring Cloud 微服务架构与 AI Agent 应用落地。

- 🔭 参与过**物流运力调度平台**、**数字化移交管理系统**、**基建智慧工程管控平台**等企业级项目的后端开发
- 🌱 正在深入学习 **Spring AI**、**RAG 系统**、**MCP 协议**及 AI Agent 工程化实践
- ✍️ 坚持技术输出，通过知识库沉淀学习笔记与项目经验

**技术栈**

| 方向 | 技术 |
|------|------|
| 后端 | Java · Spring Boot · Spring Cloud · MyBatis-Plus |
| 中间件 | Kafka · RocketMQ · Redis · Nacos · Sentinel |
| 数据库 | MySQL · Redis |
| 前端 | VitePress · Vue 3（基础） |
| AI | LLM · RAG · Spring AI · MCP · LangChain4j（学习/实践） |
| DevOps | Docker · GitHub Actions · Linux |
| 自动化 | Python · feedparser · httpx · BeautifulSoup |

---

## 🏗️ 参与项目

> 以下项目均为生产环境落地的企业级应用，我在其中负责后端开发与系统设计。

### 🚛 赫兹运力平台系统

*Spring Boot · Spring Cloud · Kafka · Redis · MySQL · Sentinel*

物流运力调度平台，支撑多运力方接入、运单调度、费用结算等核心业务流程。

| 挑战 | 方案 |
|------|------|
| 日均万级运单实时调度 | Kafka 异步削峰 + Redis 缓存热点数据 |
| 多方运力协议适配 | 统一接入网关 + SPI 扩展 |
| 分布式事务一致性 | 本地消息表 + 定时对账 |
| 高可用保障 | Sentinel 限流降级 + 熔断 |

🔗 [查看项目详情 →](https://zengchuanzc.github.io/knowledge-base/projects/hezi-transport)

---

### 📄 数字化移交通道管理平台

*Spring Boot · RocketMQ · Redis · Vue 3*

面向工程项目的资料移交与审批管理平台，实现多方协同、文件流转、审计追溯。

| 挑战 | 方案 |
|------|------|
| 复杂审批流程编排 | 工作流引擎 + 自定义任务监听器 |
| 多角色权限控制 | RBAC 权限模型 |
| 文件传输审计 | 全链路日志 + MD5 校验 |
| 跨部门数据同步 | RocketMQ 事务消息 |

🔗 [查看项目详情 →](https://zengchuanzc.github.io/knowledge-base/projects/digital-handover)

---

### 🏗️ 基建智慧工程管控项目

*Spring Boot · 物联网接入 · 实时计算 · 大屏可视化*

施工现场智能化管控平台，对接 IoT 设备实现环境监测、人员定位、安全预警。

| 挑战 | 方案 |
|------|------|
| 海量设备数据接入 | MQTT 网关 + 协议解析层 |
| 实时预警计算 | 规则引擎 + 流式处理 |
| 多项目数据隔离 | 多租户架构 |
| 大屏实时展示 | WebSocket 推送 |

🔗 [查看项目详情 →](https://zengchuanzc.github.io/knowledge-base/projects/smart-construction)

---

## 🤖 AI 热点文章自动生成系统

每天 UTC 01:00 自动执行，一套全自动的技术文章采集、筛选、生成与发布流水线。

```
RSS 源（12 个） ──▶ 并发抓取 ──▶ 关键词过滤 ──▶ AI 评分选 Top 3 ──▶ LLM 全文生成 ──▶ 文章发布
                    feedparser       40+ 关键词      DeepSeek         结构化 7 段式       Git push
```

- 📡 **多源聚合** — Baeldung、InfoQ、GitHub Blog、开源中国等 12 个技术源，配置化扩展
- 🤖 **AI 精选** — 关键词快筛 + DeepSeek 语义评分，从日均近千篇文章中精选 Top 3
- ✍️ **深度生成** — 每篇文章自动输出：摘要 · 核心内容 · 技术亮点 · 深度思考（300+ 字）
- 🔄 **全自动闭环** — 抓取 → 过滤 → 生成 → 建站，零人工干预

📖 [系统文档 →](https://github.com/ZengChuanzc/knowledge-base/tree/master/news-bot) &nbsp;|&nbsp; 📰 [浏览文章 →](https://zengchuanzc.github.io/knowledge-base/articles/)

---

## 📚 知识体系

| 领域 | 内容 | 入口 |
|------|------|------|
| ☕ **Java 后端** | JDK 8~21 新特性、JVM 原理、并发编程、Spring 生态 | [进入 →](https://zengchuanzc.github.io/knowledge-base/java/) |
| 🤖 **AI Agent** | LLM 基础、RAG、Spring AI、MCP 协议、Prompt Engineering | [进入 →](https://zengchuanzc.github.io/knowledge-base/ai-agent/) |
| 🏗️ **项目实践** | 三个企业级项目的完整文档与复盘 | [进入 →](https://zengchuanzc.github.io/knowledge-base/projects/) |
| 📰 **热点文章** | AI 自动生成，每天更新前沿技术解读 | [进入 →](https://zengchuanzc.github.io/knowledge-base/articles/) |
| 🗺️ **学习路线** | Java 后端 · AI/LLM 学习路径 | [进入 →](https://zengchuanzc.github.io/knowledge-base/roadmap/) |

---

## 🚀 本地体验

```bash
# 浏览知识库
npm install
npm run dev        # → http://localhost:5173/knowledge-base/

# 构建生产版本
npm run build
```

---

## ⭐ Star

如果对你有所帮助，欢迎 Star 支持，感谢！

<p align="center">
  <a href="https://github.com/ZengChuanzc/knowledge-base/stargazers">
    <img src="https://img.shields.io/github/stars/ZengChuanzc/knowledge-base?style=for-the-badge&logo=github&color=gold" alt="Stars">
  </a>
  <a href="https://github.com/ZengChuanzc/knowledge-base/fork">
    <img src="https://img.shields.io/github/forks/ZengChuanzc/knowledge-base?style=for-the-badge&logo=github&color=blue" alt="Forks">
  </a>
</p>

📢 **正在关注**：AI Agent 工程化 · Spring AI 实践 · RAG 系统 · Java 虚拟线程

---

<br>

<p align="center">
  <strong>学无止境 · 行以致远</strong><br>
  <sub>持续更新中</sub>
</p>
