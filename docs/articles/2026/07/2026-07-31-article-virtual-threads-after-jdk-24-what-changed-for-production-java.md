---
title: Article： Virtual Threads After JDK 24: What Changed for Production Java
date: "2026-07-31"
tags: [技术热点]
category: 技术热点
source: InfoQ
author: Sandeep Bharadwaj
---

# Article ： Virtual Threads After JDK 24: What Changed for Production Java

## 📝 一句话总结

（暂无）

---

## 📌 核心内容

```json
{
  "title": "🔥 JDK 24 后 Virtual Thread 生产环境实战：瓶颈已转移，你的代码准备好了吗？",
  "tags": ["Java", "Virtual Thread", "JDK 24", "JDK 25", "Spring Boot", "性能优化", "高并发", "架构设计"],
  "category": "技术热点",
  "one_sentence": "JDK 24 移除了虚拟线程在监视器上的 carrier-thread pinning 问题，但瓶颈已转移至下游资源饱和，生产环境必须显式进行有界化（Bounding）设计。",
  "core_content": "## 核心内容\n\n- **🧵 JDK 24 关键修复**：彻底移除了 `synchronized` 监视器导致的 carrier-thread pinning 问题，解决了 Netflix 等团队在 Java 21 上遇到的虚拟线程阻塞底层平台线程的痛点。\n- **🎯 瓶颈转移**：pinning 问题解决后，新的瓶颈不再是线程阻塞，而是 **下游资源饱和**（如数据库连接池、HTTP 客户端连接池、磁盘 I/O 队列等）。\n- **⚠️ 新的失败模式**：虚拟线程可以无限创建，导致下游系统被瞬时请求洪峰冲垮，表现为连接超时、拒绝服务、级联故障。\n- **🔧 核心解法**：必须在应用代码中 **显式引入有界化（Bounding）机制**，对下游资源进行限流和隔离，而不是依赖线程池的隐式限制。\n- **📊 实践验证**：文章基于公开基准测试，给出了从 Java 21 迁移到 JDK 24/25 后，应对新瓶颈的推荐实践序列（如使用 `Semaphore` 或定制化连接池）。",
  "why_worth": "## 为什么值得关注\n\n对于所有正在或计划在生产环境使用 Virtual Thread 的 Java 开发者来说，这篇文章是一份**及时的地图**。\n\n- **🚨 打破认知误区**：很多开发者以为 JDK 21 发布虚拟线程后，`synchronized` 就完全不能用了。JDK 24 的修复让这一限制成为历史，这改变了我们编写并发代码的方式。\n- **📈 直面真实挑战**：文章没有停留在“虚拟线程很牛”的层面，而是精准指出了迁移后真正会遇到的“坑”——下游资源饱和。这比单纯介绍 API 更有价值。\n- **🛠️ 实战指导意义**：它给出了一个清晰的信号：**虚拟线程不是银弹**。它解决了“线程阻塞”的旧问题，却把压力转移到了“资源规划”的新问题上，这要求架构师必须有全局的资源预算意识。",
  "tech_highlights": "## 技术亮点\n\n- **新增功能/修复**：JDK 24 (JEP 491) 移除了 `synchronized` 在虚拟线程中的 pinning 限制，这是自虚拟线程诞生以来最重要的运行时改进。\n- **架构变化**：从“线程池限制并发”的旧架构，转向“无限制线程 + 显式资源信号量”的新架构。`Semaphore` 和 `RateLimiter` 成为核心并发原语。\n- **性能优化**：消除了平台线程被无谓占用的场景，使得在相同硬件下，系统吞吐量上限更高，但同时也对下游服务的承压能力提出了更高要求。\n- **最佳实践**：\n  - **有界化一切**：数据库连接池、Redis 连接池、外部 API 调用必须设置严格的 `maxTotal` 和 `maxWait`。\n  - **引入背压机制**：使用 `Semaphore` 控制进入业务逻辑的并发数，防止无限创建虚拟线程。\n  - **超时与熔断**：所有下游调用必须配置合理的超时时间，并配合 `Resilience4j` 等熔断器。\n- **API 变化**：虽然核心 API 未变，但 `Thread.Builder` 的使用模式推荐从 `ofVirtual()` 配合 `ExecutorService` 转向更精细的 `Semaphore` 控制。\n- **兼容性**：JDK 24/25 对 Java 21 代码完全兼容，但需要重新审视依赖注入容器（如 Spring）中关于线程池的配置策略。",
  "my_thoughts": "## 我的思考\n\n作为一个 Java 后端工程师，读完这篇文章后我最大的感受是：**虚拟线程终于真正走向成熟了，但我们的编程思维必须随之升级。**\n\n**是否值得学习？** 绝对值得。这是 Java 并发领域近十年最重大的变革。JDK 24 的修复让虚拟线程在几乎所有业务场景下都可以放心使用，不再需要为了避开 `synchronized` 而刻意使用 `ReentrantLock`，代码可以回归最朴素的写法。\n\n**适用于哪些场景？** 它最适合 **IO密集型** 应用，特别是微服务网关、BFF层、数据聚合服务。在这些场景下，虚拟线程能轻松支撑上万并发连接，而系统资源占用极低。但对于 **CPU密集型** 任务（如复杂计算、加解密），虚拟线程没有优势，依然需要依赖 `ForkJoinPool` 或手动控制并行度。\n\n**未来趋势？** 我认为 JDK 25 LTS 将是虚拟线程真正爆发式落地的版本。随着 pinning 问题的修复，像 Tomcat、Netty 等底层框架会彻底转向虚拟线程模型。未来，`ExecutorService` 可能会逐渐淡出业务代码，取而代之的是结构化并发（JEP 453）和显式的资源管理。\n\n**是否值得生产环境使用？** 非常值得，但必须带着敬畏之心。正如文章所说，**瓶颈转移了**。在 Java 21 时代，我们要防的是线程池耗尽；在 JDK 24+ 时代，我们要防的是数据库连接池被瞬间打满。我建议团队在生产环境引入虚拟线程时，必须同步引入 `Semaphore` 对关键链路做信号量隔离，并且要压测下游服务能承受的最大 QPS，做到心中有数。\n\n**与 Spring AI 是否有关？** 关系很大。Spring AI 的核心场景是调用外部大模型 API，这属于典型的 IO 密集型操作（需要等待网络响应）。使用虚拟线程替代传统线程池，可以让 Spring AI 应用轻松应对大量并发用户请求，而不会因为线程数过多导致 OOM。\n\n**是否可以结合 RAG？** 完全可以。在 RAG 架构中，通常包含文档解析、向量化、向量检索、LLM 生成等多个环节，其中涉及大量 IO 操作（读取文件、调用 Embedding 模型、查询向量数据库）。使用虚拟线程可以简化并发编排，例如并行执行多个文档的分块与向量化，而不必引入复杂的响应式编程模型。\n\n**是否值得后续写专题？** 非常值得。我计划在后续的专题中，基于 Spring Boot 3.4 + JDK 25 搭建一个实战项目，展示如何通过 `Semaphore` 控制虚拟线程的并发度，以及如何用 Micrometer 监控虚拟线程的状态和下游资源池的饱和度。我相信这会是一个非常有价值的系列，

## 💭 我的思考

帮助大家少踩坑。",
}
```

---

> 📎 **原文链接**: [https://www.infoq.com/articles/virtual-threads-after-jdk24/?utm_campaign=infoq_content&utm_source=infoq&utm_medium=feed&utm_term=global](https://www.infoq.com/articles/virtual-threads-after-jdk24/?utm_campaign=infoq_content&utm_source=infoq&utm_medium=feed&utm_term=global)

> 📅 **文章日期**: 2026-08-02
> 🏷️ **标签**: 技术热点
> 📂 **分类**: 技术热点
