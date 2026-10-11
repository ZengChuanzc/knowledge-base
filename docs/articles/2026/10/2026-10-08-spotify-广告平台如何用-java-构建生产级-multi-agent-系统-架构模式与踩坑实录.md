---
title: "Spotify 广告平台如何用 Java 构建生产级 Multi-Agent 系统：架构模式与踩坑实录"
date: "2026-10-08"
tags: ["Java", "Multi-Agent", "Google ADK", "AI Agent", "Spotify", "架构设计", "LLM", "分布式系统"]
category: "技术热点"
source: "InfoQ"
description: "Spotify 广告平台工程师分享基于 Google ADK Java 构建生产级多智能体系统的架构模式，涵盖领域所有权、确定性护栏、追踪评估等核心经验，为 Java 开发者提供 Agent 边界划分与成本优化的实战指南。"
author: "Pratik Rasam"
---

# Spotify 广告平台如何用 Java 构建生产级 Multi-Agent 系统：架构模式与踩坑实录

## 📝 一句话总结

Spotify 广告平台工程师分享基于 Google ADK Java 构建生产级多智能体系统的架构模式，涵盖领域所有权、确定性护栏、追踪评估等核心经验，为 Java 开发者提供 Agent 边界划分与成本优化的实战指南。

---

## 📌 核心内容

- **🏗️ 多智能体架构模式**：Spotify Ads Manager 在生产环境中运行了基于 Google ADK（Agent Development Kit）Java 的多智能体系统，采用多个专职 Agent 协同工作，而非构建单体 Agent（Monolithic Agent）
- **🎯 领域所有权模型（Domain Ownership）**：每个 Agent 拥有明确的业务领域边界，类似微服务中的 Bounded Context 概念，避免职责重叠和相互干扰
- **🛡️ 确定性护栏（Deterministic Guardrails）**：在 LLM 的不确定性输出之上，叠加确定性的业务规则校验层，确保广告投放等关键业务的可靠性
- **🔍 基于追踪的评估策略（Tracing-based Evaluation）**：通过全链路 Tracing 对 Agent 的决策过程进行评估和调试，而非仅看最终输出结果
- **⚙️ 工具 Schema 优化**：精心设计 Agent 可调用的 Tool Schema，减少 Token 消耗并提升调用准确率
- **💰 成本管理**：在多 Agent 协作场景下，通过合理的 Agent 边界划分和调用链路设计来控制 LLM 调用成本
- **🚫 避免单体 Agent 陷阱**：单体 Agent 在复杂业务场景下会出现 Prompt 膨胀、工具过多导致选择困难、调试困难等问题
- **☕ Java 技术栈落地**：使用 Google ADK Java 实现，证明了 Java 生态在 AI Agent 领域的可行性

## 🎯 为什么值得关注

- **Java 开发者的 AI 落地范本**：当前 AI Agent 领域 Python 占据主导，但 Spotify 用 Java + Google ADK 在生产环境跑通了多智能体系统，这对广大 Java 后端工程师极具参考价值
- **从 Demo 到生产的真实经验**：大多数 Agent 文章停留在概念验证阶段，而本文来自 Spotify 广告平台的生产实践，包含大量"踩坑"经验
- **架构思维的迁移**：多 Agent 的领域所有权模型与微服务架构中的服务拆分思路高度相似，Java 工程师可以快速将已有的分布式系统经验迁移过来
- **成本与可靠性的平衡**：广告平台对成本和可靠性要求极高，Spotify 的实践为如何在生产环境中控制 LLM 成本提供了可借鉴的方案
- **Google ADK Java 生态**：了解 Google ADK Java 的能力边界，评估是否适合引入到自己的技术栈中

## ✨ 技术亮点

### 🆕 新增功能 / 技术栈
- **Google ADK Java**：Google 推出的 Agent Development Kit 的 Java 版本，提供了 Agent 定义、Tool 注册、多 Agent 编排等核心能力
- **Tracing-based Evaluation**：将可观测性（Observability）理念引入 Agent 评估，通过 Trace 还原 Agent 的完整决策链路

### 🏛️ 架构变化
- **从单体 Agent 到多 Agent 协作**：类似于从单体应用向微服务演进，每个 Agent 专注特定领域
- **Domain Ownership 模型**：Agent 边界划分参考领域驱动设计（DDD），每个 Agent 拥有独立的工具集和知识范围
- **确定性护栏层**：在 LLM 输出之后增加业务规则引擎校验，形成"LLM 生成 + 规则校验"的双层保障

### ⚡ 性能优化
- **Tool Schema 精简**：减少每个 Tool 的参数数量和描述长度，降低 Token 消耗
- **Agent 边界优化**：合理的边界划分减少不必要的 Agent 间通信，降低延迟和成本

### 📋 最佳实践
- 绘制 Agent 边界时参考业务领域而非技术功能
- 为每个 Agent 定义清晰的输入输出契约
- 使用 Tracing 进行端到端的 Agent 行为评估
- 在生产环境中始终保留确定性护栏
- 定期审查 Tool Schema 的 Token 开销

### 🔌 API 变化
- Google ADK Java 提供了声明式的 Agent 定义 API，支持通过 Builder 模式构建 Agent
- Tool 注册采用注解 + Schema 自动生成的方式

### 🔄 兼容性
- 基于 Java 生态，可与 Spring Boot 等主流框架集成
- 支持与现有的可观测性体系（如 OpenTelemetry）对接

## 💭 我的思考

作为一个在 Java 后端摸爬滚打多年的工程师，看到 Spotify 用 Java 在生产环境落地 Multi-Agent 系统，说实话是有些兴奋的。

**是否值得学习？** 非常值得。当前 AI Agent 的讨论几乎被 Python 生态垄断，LangChain、CrewAI、AutoGen 等框架清一色 Python。但企业级后端系统绝大多数跑在 Java 上，如果 Agent 能力无法融入 Java 技术栈，那 AI 落地就永远是"Python 做 Demo，Java 做集成"的尴尬局面。Spotify 的实践证明了 Java + Google ADK 这条路是走得通的。

**适用于哪些场景？** 多 Agent 架构特别适合业务域复杂、需要多步骤决策的场景，比如广告投放优化、风控审批流、智能客服路由、供应链调度等。如果你的业务只需要简单的 LLM 调用（如文本摘要、分类），那单 Agent 甚至直接调 API 就够了，没必要上多 Agent 增加复杂度。

**与 Spring AI 的关系？** 这是我最关心的问题。Spring AI 目前更偏向于 LLM 调用的抽象层（ChatClient、Embedding、VectorStore 等），在 Agent 编排方面还在发展中。Google ADK Java 则更专注于 Agent 的定义、编排和工具调用。两者并非互斥——完全可以用 Spring AI 做底层 LLM 接入和 RAG，用 ADK 做上层 Agent 编排。未来如果 Spring AI 推出成熟的 Agent 模块，可能会形成竞争，但短期内互补大于竞争。

**是否可以结合 RAG？** 当然可以，而且应该结合。每个 Agent 可以挂载自己的知识库（VectorStore），通过 RAG 获取领域知识。比如广告投放 Agent 可以 RAG 检索历史投放数据、行业基准、平台政策等。关键是要为每个 Agent 设计独立的 RAG 管道，避免知识污染。

**是否值得在生产环境使用？** 我的判断是：如果你的团队已经有 Java 微服务架构，且业务场景确实需要多步骤 AI 决策，可以小范围试点。但要注意几点：一是 Google ADK Java 还比较新，API 可能不稳定；二是多 Agent 的调试和可观测性比微服务更复杂，因为 LLM 的输出是不确定的；三是成本控制需要从第一天就重视。

**未来趋势？** 我判断未来 1-2 年会出现以下趋势：一是 Java AI Agent 框架会迎来爆发，Spring AI、Quarkus AI、Google ADK Java 等会快速迭代；二是 Multi-Agent 的架构模式会逐渐标准化，类似微服务的 Service Mesh，可能会出现 Agent Mesh；三是 Agent 的可观测性和评估会成为独立的技术领域。

**是否值得后续写专题？** 非常值得。我计划后续写一个系列，包括：用 Spring Boot + Google ADK Java 搭建多 Agent 系统的实战教程、Agent 边界划分的方法论、基于 OpenTelemetry 的 Agent Tracing 实践、以及 Multi-Agent 系统的成本优化策略。这个方向内容深度足够，实战价值高，值得深入挖掘。

总之，Spotify 的这次分享给 Java 社区打了一剂强心针——AI Agent 不是 Python 的专利，Java 工程师同样可以在这个领域大展拳脚。关键是要把我们在分布式系统、微服务架构中积累的经验迁移过来，同时正视 LLM 带来的不确定性挑战。

---

> 📎 **原文链接**: [https://www.infoq.com/presentations/spotify-multi-agent-ai-architecture/?utm_campaign=infoq_content&utm_source=infoq&utm_medium=feed&utm_term=global](https://www.infoq.com/presentations/spotify-multi-agent-ai-architecture/?utm_campaign=infoq_content&utm_source=infoq&utm_medium=feed&utm_term=global)

> 📅 **文章日期**: 2026-10-11
> 🏷️ **标签**: Java, Multi-Agent, Google ADK, AI Agent, Spotify, 架构设计, LLM, 分布式系统
> 📂 **分类**: 技术热点
