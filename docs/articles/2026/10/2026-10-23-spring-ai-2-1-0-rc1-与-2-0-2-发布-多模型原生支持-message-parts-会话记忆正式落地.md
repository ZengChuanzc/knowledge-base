---
title: "Spring AI 2.1.0-RC1 与 2.0.2 发布：多模型原生支持 Message Parts，会话记忆正式落地"
date: "2026-10-23"
tags: ["Java", "Spring Boot", "Spring AI", "AI 集成", "LLM", "RAG", "多模型适配"]
category: "技术热点"
source: "Spring Blog"
description: "Spring AI 2.1.0-RC1 实现主流大模型原生支持 Message Parts 和会话记忆，并新增工具调用确认与预计算向量检索，大幅提升多模型 AI 应用开发体验。"
author: "ebottard"
---

# Spring AI 2.1.0-RC1 与 2.0.2 发布：多模型原生支持 Message Parts，会话记忆正式落地

## 📝 一句话总结

Spring AI 2.1.0-RC1 实现主流大模型原生支持 Message Parts 和会话记忆，并新增工具调用确认与预计算向量检索，大幅提升多模型 AI 应用开发体验。

---

## 📌 核心内容

- **Message Parts 跨提供商原生支持**：在 2.1.0-M1 中，仅 `OpenAiResponsesChatModel` 原生支持 `MessagePart` 内容；本次 RC1 将支持范围扩展至 OpenAI (Chat Completions)、Anthropic、Google GenAI、Amazon Bedrock Converse、Ollama、Mistral AI、DeepSeek 等主流 `ChatModel` 实现，确保推理过程、工具调用及提供商特有块保持原始顺序和不透明负载。
- **会话记忆（Session Memory）内置**：Spring AI 自身开始提供会话记忆能力，开发者无需自行维护对话上下文，简化多轮对话应用的开发。
- **工具调用确认（Tool Call Confirmation）**：新增工具调用确认机制，允许在调用外部工具前进行人工或程序化确认，提升安全性与可控性。
- **预计算嵌入支持扩展**：在原有预计算嵌入基础上，新增按查询向量进行搜索的能力，进一步完善 RAG 场景下的向量检索支持。
- **版本升级路径清晰**：2.1.0-RC1 基于 2.1.0-M1 构建，兑现了“What's next”中的大部分承诺；同时 2.0.2 作为稳定维护版本同步发布，提供升级说明和参考文档。

## 🎯 为什么值得关注

- **多模型统一抽象再进一步**：Spring AI 一直致力于屏蔽不同大模型提供商的差异。本次 Message Parts 的跨提供商原生支持，意味着开发者可以在不改变业务代码的前提下，自由切换 OpenAI、Anthropic、Google、Bedrock、Ollama 等模型，并保留推理链、工具调用等复杂消息结构。
- **会话记忆开箱即用**：对于构建聊天机器人、智能客服等需要多轮对话的应用，内置的 Session Memory 省去了大量样板代码，降低了 Spring 生态下 AI 应用的入门门槛。
- **安全与可控性增强**：工具调用确认机制让 AI Agent 在调用外部 API 或执行敏感操作前有机会被拦截，这对生产环境至关重要。
- **RAG 能力持续完善**：预计算嵌入的查询向量搜索扩展，使得基于 Spring AI 构建 RAG 应用更加灵活高效。
- **Spring 生态无缝集成**：对于已经使用 Spring Boot 的团队，Spring AI 提供了最自然的 AI 集成方式，无需引入额外框架，保持技术栈统一。

## ✨ 技术亮点

- **新增功能**：
  - 跨提供商的 `MessagePart` 原生生产与消费，覆盖 OpenAI、Anthropic、Google GenAI、Amazon Bedrock Converse、Ollama、Mistral AI、DeepSeek。
  - 内置 Session Memory，支持多轮对话上下文管理。
  - 工具调用确认（Tool Call Confirmation）机制。
  - 预计算嵌入支持按查询向量搜索。
- **架构变化**：
  - 消息抽象层进一步统一，各 `ChatModel` 实现直接处理 `MessagePart`，减少适配层转换损耗。
  - 会话记忆从外部组件下沉至 Spring AI 核心，简化架构。
- **性能优化**：
  - 原生 Message Parts 处理避免了消息结构的序列化/反序列化开销，保持原始顺序与不透明负载，提升推理与工具调用的准确性。
  - 预计算嵌入的查询向量搜索优化了 RAG 检索路径。
- **最佳实践**：
  - 使用统一的 `ChatModel` 接口配合 `MessagePart` 构建多模型应用。
  - 利用 Session Memory 管理对话状态，避免手动维护历史消息。
  - 对敏感工具调用启用确认机制，确保生产安全。
- **API 变化**：
  - `MessagePart` 成为一等公民，各 `ChatModel` 实现需支持其生产与消费。
  - 新增会话记忆相关 API 和工具调用确认 API。
- **兼容性**：
  - 2.1.0-RC1 基于 2.1.0-M1，升级路径平滑；2.0.2 为稳定维护版本，适合生产环境逐步迁移。
  - 提供详细的升级说明和参考文档，降低迁移成本。

## 💭 我的思考

作为一名长期使用 Spring Boot 的 Java 后端工程师，Spring AI 的这次发布让我感到兴奋。首先，**是否值得学习？** 答案是肯定的。Spring AI 正在快速迭代，逐步补齐生产级 AI 应用所需的关键能力。Message Parts 的跨提供商原生支持意味着我们可以用一套代码对接多个大模型，这在模型选型频繁变化的今天极具价值。会话记忆的内置更是解决了多轮对话中的痛点，减少了重复造轮子的成本。

**适用于哪些场景？** 我认为最直接的场景是构建企业级智能客服、知识库问答（RAG）、AI Agent 工作流等。尤其是需要切换不同模型提供商（如因成本、合规或性能考虑）的团队，Spring AI 的统一抽象能显著降低适配工作量。工具调用确认机制则非常适合金融、医疗等对操作安全要求高的领域。

**未来趋势？** 大模型应用开发正从“单模型调用”走向“多模型编排与 Agent 协作”。Spring AI 的演进方向与这一趋势吻合：统一消息抽象、内置记忆、工具调用控制、向量检索增强。可以预见，未来 Spring AI 会进一步集成更多 Agent 框架能力，甚至可能提供声明式的 AI 工作流编排。

**是否值得生产环境使用？** 2.0.2 作为稳定版本可以谨慎用于生产，但 2.1.0-RC1 仍属候选发布版，建议在非关键业务中先行验证。对于追求稳定性的团队，可以等待 2.1.0 正式版。不过，RC1 中新增的 Message Parts 和会话记忆功能已经足够吸引人，值得在预研项目中尝试。

**与 Spring AI 是否有关？** 本文本身就是 Spring AI 的发布说明，自然密切相关。对于已经使用 Spring Boot 的团队，引入 Spring AI 几乎零成本，且能享受 Spring 生态的依赖注入、配置管理、可观测性等便利。

**是否可以结合 RAG？** 当然可以。本次预计算嵌入的查询向量搜索扩展直接服务于 RAG 场景。结合 Spring AI 的 VectorStore 抽象，开发者可以轻松构建检索增强生成应用。未来如果 Spring AI 能进一步集成文档加载、分块、重排序等 RAG 全链路组件，将更加完善。

**是否值得后续写专题？** 非常值得。Spring AI 的更新节奏快，且涉及多模型适配、Agent、RAG 等热点话题。我计划后续撰写系列文章，深入分析 Message Parts 的实现原理、Session Memory 的设计、工具调用确认的实战用法，以及如何基于 Spring AI 构建生产级 RAG 应用。对于 Java 开发者而言，掌握 Spring AI 将成为 AI 时代的重要竞争力。

---

> 📎 **原文链接**: [https://spring.io/blog/2026/10/23/spring-ai-2-1-0-RC1-available-now](https://spring.io/blog/2026/10/23/spring-ai-2-1-0-RC1-available-now)

> 📅 **文章日期**: 2026-10-25
> 🏷️ **标签**: Java, Spring Boot, Spring AI, AI 集成, LLM, RAG, 多模型适配
> 📂 **分类**: 技术热点
