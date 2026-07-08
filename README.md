<p align="center">
  <img alt="Knowledge Base" src="https://zengchuanzc.github.io/knowledge-base/k-icon.svg" width="64">
</p>

<h1 align="center">ZengChuan's Engineering Knowledge Base</h1>

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
    <img src="https://zengchuanzc.github.io/knowledge-base/img/index.png" alt="知识库首页截图" width="720" style="border-radius: 8px; border: 1px solid #e2e8f0;">
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

4 年 Java 后端开发经验，专注于 Spring Boot / Spring Cloud 微服务架构与 AI Agent 应用落地。

- 🔭 参与过**赫兹运力平台**（400万+ 运单）、**数字化移交管理平台**（AI Code Review）、**基建智慧工程管控项目**（30-40万用户）等企业级项目
- 🌱 正在深入学习 **Spring AI**、**RAG 系统**、**MCP 协议**及 AI Agent 工程化实践
- ✍️ 坚持技术输出，通过知识库沉淀学习笔记与项目经验

| 方向 | 技术 |
|------|------|
| 后端 | Java · Spring Boot · Spring Cloud · MyBatis-Plus |
| 中间件 | Kafka · RocketMQ · Redis · Nacos · Sentinel |
| 数据库 | MySQL |
| AI | Qwen · LangChain4j · RAG · Spring AI · MCP |
| DevOps | Docker · Jenkins · GitHub Actions · Linux |

---

## 🏗️ 项目实践

### 🚛 赫兹运力平台系统

`Spring Boot` `Spring Cloud` `MySQL` `Redis` `RocketMQ` `Nacos` `Docker`

面向电力物资运输场景的企业级运力管理平台，覆盖 App、PC、小程序三端，支撑运营、司机、承运商多角色协同。

- **规模**：累计处理 **400 万+ 运单**
- **我的角色**：参与系统重构及新旧系统切换
- **核心贡献**：
  - 高频报表查询 **1.2s → 200ms**（SQL 优化 + 缓存 + 架构级调整）
  - RocketMQ 异步化 + 策略模式重构报表生成，解决接口长时间阻塞
  - 主导报表中心异步化改造，实现业务解耦

📄 [查看完整技术方案 →](https://zengchuanzc.github.io/knowledge-base/projects/hezi-transport)

---

### 📄 数字化移交通道管理平台

`Spring Boot` `Spring Cloud Alibaba` `MySQL` `Redis` `Qwen` `LangChain4j`

面向大型集团工程全生命周期移交场景的双模块（外网+内网）分布式管理平台。

- **规模**：建设、施工、监理、管理多单位协同
- **我的角色**：主导架构搭建 + 制定开发规范 + 统筹 **60%+ 核心功能交付**
- **核心贡献**：
  - 基于 Qwen + LangChain4j 开发 **AI Code Review** 组件，误报率 **22% → 9%**
  - BPMS 多节点审核流程开发，审核效率提升 **40%**
  - Git Webhook + Embedding 检索 + Few-shot Prompt 工程实践

📄 [查看完整技术方案 →](https://zengchuanzc.github.io/knowledge-base/projects/digital-handover)

---

### 🏗️ 基建智慧工程管控项目

`Spring Boot` `Spring Cloud` `MySQL` `Redis` `Kafka` `RocketMQ` `Docker` `Jenkins`

服务 **30-40 万用户**的企业级基建工程管控平台，涵盖工程、进度、安全三大中心。

- **规模**：30-40 万用户，项目周期三年
- **我的角色**：后端开发与性能优化
- **核心贡献**：
  - **Redis + Caffeine 多级缓存**：高频接口（日均 120 万次）**700ms → 100ms**，P99 **2.1s → 210ms**
  - **Kafka + MyBatis 动态分表路由**：解决多省份设备监控数据单表膨胀
  - **RocketMQ 异步消息驱动**：进度编制接口 **1.5s → 80ms**
  - 千万级数据量年度统计性能提升 **70%**（SQL 重写 + 索引优化 + 多线程并行）

📄 [查看完整技术方案 →](https://zengchuanzc.github.io/knowledge-base/projects/smart-construction)

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
| 🏗️ **项目实践** | 三个企业级项目的完整技术方案与复盘 | [进入 →](https://zengchuanzc.github.io/knowledge-base/projects/) |
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
