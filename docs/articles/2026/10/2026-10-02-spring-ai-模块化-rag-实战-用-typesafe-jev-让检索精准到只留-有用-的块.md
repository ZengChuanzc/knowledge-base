---
title: "Spring AI 模块化 RAG 实战：用 TypeSafe Jev 让检索精准到只留“有用”的块"
date: "2026-10-02"
tags: ["Java", "Spring AI", "RAG", "TypeSafe Jev", "Modular RAG", "向量数据库", "LLM", "后端架构"]
category: "技术热点"
source: "Spring Blog"
description: "Spring AI 的 Modular RAG 结合 TypeSafe Jev，通过两次 LLM 调用优化用户问题，再用 Jev 对每个检索块做相关性判定，显著提升 RAG 精准度。"
author: "tzolov"
---

# Spring AI 模块化 RAG 实战：用 TypeSafe Jev 让检索精准到只留“有用”的块

## 📝 一句话总结

Spring AI 的 Modular RAG 结合 TypeSafe Jev，通过两次 LLM 调用优化用户问题，再用 Jev 对每个检索块做相关性判定，显著提升 RAG 精准度。

---

## 📌 核心内容

- **痛点直击**：经典 `QuestionAnswerAdvisor` + 向量库的朴素 RAG 容易把无关块塞进 prompt，导致幻觉和 token 浪费。
- **解决方案**：`JevDocumentFilter` 和 `JevDocumentReranker` 作为 `DocumentPostProcessor`，可直接插入 Spring AI 的 Modular RAG 管道。
- **双 LLM 调用**：在检索前用两次 LLM 调用对用户原始问题进行“清洗”和“扩展”，提升召回质量。
- **Jev 判定**：检索后，Jev 对每个 chunk 进行评分/判定，只保留真正能回答问题的内容，再送入 prompt。
- **一站式配置**：整个管道通过一个 advisor builder 组装，代码简洁，与现有 Spring AI 生态无缝集成。
- **Demo 对比**：官方提供 `05-1-modular-rag` 模块，与朴素版 `05-rag` 并列，可直接 diff 运行效果。

## 🎯 为什么值得关注

- **RAG 是当前 LLM 应用落地的核心模式**，但朴素 RAG 的“检索即塞入”策略在生产环境经常翻车。Spring AI 官方给出的 Modular RAG + Jev 方案，提供了一条可插拔、可量化的优化路径。
- **对 Java 开发者友好**：不用切换到 Python 生态，直接在 Spring Boot 项目里用熟悉的 `Advisor`、`DocumentPostProcessor` 等抽象完成高级 RAG 编排。
- **TypeSafe Jev 的“校准数字”特性**：让相关性判定不再依赖模糊的相似度分数，而是有明确语义的判定结果，便于调试和监控。
- **模块化设计**：`JevDocumentFilter` 和 `JevDocumentReranker` 可以单独使用，也可以组合，灵活适配不同场景。
- **官方 Demo 可复现**：文章引用的输出均来自真实运行，不是纸上谈兵，降低了学习门槛。

## ✨ 技术亮点

- **新增组件**：`JevDocumentFilter` 与 `JevDocumentReranker` 作为 `DocumentPostProcessor` 的实现，直接嵌入 Modular RAG 管道。
- **架构变化**：从“单一 Advisor 直连向量库”升级为“问题优化 → 检索 → Jev 判定 → prompt 组装”的多阶段管道。
- **性能优化**：通过过滤无关 chunk，减少 prompt token 消耗，同时降低幻觉概率；两次 LLM 调用虽增加延迟，但换来更高召回质量。
- **最佳实践**：官方推荐将 Modular RAG 与朴素 RAG 并列对比（`05-1-modular-rag` vs `05-rag`），便于评估收益。
- **API 变化**：通过 advisor builder 统一编排，减少手动拼接 `QuestionAnswerAdvisor` 的样板代码。
- **兼容性**：基于 Spring AI 现有抽象，不破坏既有 RAG 流程，可渐进式迁移。

## 💭 我的思考

作为一名长期在 Java 后端一线搬砖的工程师，看到 Spring AI 把 Modular RAG 和 TypeSafe Jev 组合起来，第一反应是“终于有人把 RAG 的脏活累活标准化了”。

**是否值得学习？** 非常值得。RAG 不是新概念，但如何在 Java 生态里优雅地实现“检索-过滤-重排-生成”闭环，一直是痛点。Spring AI 的 `DocumentPostProcessor` 抽象让过滤和重排变成可插拔组件，Jev 则提供了语义级的判定能力。这套组合拳比自己在业务代码里写 if-else 过滤 chunk 要靠谱得多。

**适用于哪些场景？** 知识库问答、客服机器人、文档摘要、代码助手等所有需要“基于私有数据回答”的场景。尤其是对答案准确性要求高、且 token 成本敏感的 to B 应用。

**未来趋势？** 我判断 RAG 会走向“模块化 + 可评估”。单纯向量检索的时代会过去，检索前的问题改写、检索后的重排与过滤会成为标配。Spring AI 这次把 Jev 作为 TypeSafe 的延伸，说明官方也在探索“可量化”的 RAG 质量评估。

**是否值得生产环境使用？** 谨慎乐观。两次 LLM 调用会带来额外延迟和成本，需要结合业务 QPS 和 SLA 评估。但 Jev 的判定如果足够快（文章提到几百毫秒），且能显著减少 prompt token，总体成本可能反而下降。建议先在非核心链路灰度。

**与 Spring AI 是否有关？** 这就是 Spring AI 官方博客的内容，属于核心生态的一部分。`JevDocumentFilter` 和 `JevDocumentReranker` 是 Spring AI 的扩展点，不是第三方 hack。

**是否可以结合 RAG？** 本身就是 RAG 的增强方案，而且是模块化 RAG 的典型实践。

**是否值得后续写专题？** 非常值得。可以围绕“Modular RAG 在 Spring Boot 中的落地”写系列：问题改写策略、Jev 判定阈值调优、与不同向量库的集成、性能压测对比等。建议先跑通 `05-1-modular-rag` Demo，再逐步替换成自己的业务数据，积累调优经验。

总之，这套方案给 Java 后端工程师提供了一个不依赖 Python 生态的高级 RAG 工具箱，值得投入时间研究。

---

> 📎 **原文链接**: [https://spring.io/blog/2026/10/02/spring-ai-modular-rag-typesafe-jev](https://spring.io/blog/2026/10/02/spring-ai-modular-rag-typesafe-jev)

> 📅 **文章日期**: 2026-10-04
> 🏷️ **标签**: Java, Spring AI, RAG, TypeSafe Jev, Modular RAG, 向量数据库, LLM, 后端架构
> 📂 **分类**: 技术热点
