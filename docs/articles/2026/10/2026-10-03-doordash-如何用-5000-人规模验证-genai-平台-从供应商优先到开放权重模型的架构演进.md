---
title: "DoorDash 如何用 5000 人规模验证 GenAI 平台：从供应商优先到开放权重模型的架构演进"
date: "2026-10-03"
tags: ["GenAI", "LLM", "Agent", "AI Gateway", "架构设计", "DoorDash", "RAG", "Spring AI"]
category: "技术热点"
source: "InfoQ"
description: "DoorDash 分享了其内部 GenAI 平台从供应商优先转向开放权重模型的架构演进，涵盖 LLM 网关、Agent 网关设计，以及在 5000+ 内部用户规模下平衡准确性、延迟与成本的核心经验。"
author: "Siddharth Kodwani, Swaroop Chitlur"
---

# DoorDash 如何用 5000 人规模验证 GenAI 平台：从供应商优先到开放权重模型的架构演进

## 📝 一句话总结

DoorDash 分享了其内部 GenAI 平台从供应商优先转向开放权重模型的架构演进，涵盖 LLM 网关、Agent 网关设计，以及在 5000+ 内部用户规模下平衡准确性、延迟与成本的核心经验。

---

## 📌 核心内容

- 🏗️ **平台定位**：DoorDash 构建了一个服务超过 5,000 名内部用户的 GenAI 平台，支撑公司内部各类 AI 应用场景
- 🔄 **架构转型**：从最初的 vendor-first（供应商优先）策略，逐步过渡到 open-weights models（开放权重模型），降低对单一供应商的依赖
- 🚪 **双网关架构**：设计了 LLM Gateway 和 Agent Gateway 两层网关，分别处理模型调用和智能体编排的流量治理
- ⚖️ **三角平衡**：在 accuracy（准确性）、latency（延迟）和 cost（成本）之间持续权衡，这是大规模 GenAI 平台的核心挑战
- 🧩 **核心架构赌注**：分享了团队在平台建设初期做出的关键架构决策及其后续影响
- 👥 **规模化验证**：5,000+ 内部用户的实际使用验证了平台架构的可行性和扩展性
- 🔀 **供应商策略**：从依赖商业 API 到自托管开放权重模型的迁移路径与经验教训

## 🎯 为什么值得关注

- 🎯 **真实大规模案例**：这不是实验室 Demo，而是服务 5,000+ 用户的生产级平台，极具参考价值
- 🏛️ **架构决策参考**：LLM Gateway + Agent Gateway 的双层网关设计，为 Java 团队构建类似平台提供了架构蓝本
- 💰 **成本控制实战**：如何在保证准确性和延迟的前提下控制成本，是所有 GenAI 落地项目必须面对的问题
- 🔧 **技术选型启示**：从 vendor-first 到 open-weights 的转型路径，帮助团队思考自己的模型选型策略
- 🌐 **网关模式与 Java 生态契合**：Gateway 模式与 Spring Cloud Gateway、Spring AI 等 Java 技术栈天然契合，Java 开发者可直接借鉴
- 📈 **行业趋势风向标**：DoorDash 的实践代表了大型互联网公司 GenAI 平台化的主流方向

## ✨ 技术亮点

### 🆕 新增功能/架构变化
- **LLM Gateway**：统一管理所有 LLM 调用，提供路由、限流、缓存、可观测性等能力
- **Agent Gateway**：专门处理 Agent 编排流量，支持多步推理、工具调用等复杂场景
- **开放权重模型自托管**：从商业 API 转向自托管开源模型，掌握更多控制权

### ⚡ 性能优化
- 在 accuracy、latency、cost 三角中寻找最优平衡点
- 通过网关层实现请求路由优化，根据场景选择不同模型
- 可能的缓存策略和批量推理优化

### 🏆 最佳实践
- **渐进式架构演进**：先 vendor-first 快速验证，再逐步迁移到开放权重模型
- **网关分层设计**：LLM Gateway 和 Agent Gateway 职责分离，避免耦合
- **规模化验证**：以 5,000+ 用户的实际负载驱动架构优化

### 🔌 API 设计
- 统一 LLM 调用接口，屏蔽底层模型差异
- Agent 编排 API 抽象，支持复杂工作流

### 🔄 兼容性
- 支持多模型供应商切换，避免 vendor lock-in
- 开放权重模型与商业模型并存，灵活切换

## 💭 我的思考

作为一名 Java 后端工程师，DoorDash 这个案例让我深受启发。

**是否值得学习？** 毫无疑问值得。DoorDash 的 GenAI 平台架构本质上是一个典型的**网关模式 + 多模型路由**问题，这与 Java 生态中 Spring Cloud Gateway、API Gateway 的设计理念一脉相承。对于正在探索 AI 落地的 Java 团队来说，这个案例提供了从 0 到 1 再到规模化的完整路径参考。

**适用于哪些场景？** 我认为特别适合以下场景：企业内部 AI 助手平台、多模型统一调用中台、需要控制 AI 成本的中大型团队、以及需要 Agent 编排能力的复杂业务场景。如果你的团队有多个业务线需要接入 LLM，但缺乏统一治理，这个架构模式可以直接借鉴。

**与 Spring AI 的关系？** 关联度极高。Spring AI 提供了 ChatClient、EmbeddingClient 等抽象，本质上就是在做 LLM Gateway 的事情。DoorDash 的 LLM Gateway 可以用 Spring AI 作为底层实现，再在其上叠加路由、限流、缓存等企业级能力。而 Agent Gateway 则可以结合 Spring AI 的 Function Calling 和 Tool 机制来构建。

**是否可以结合 RAG？** 完全可以。RAG 是企业 GenAI 落地最常见的场景，DoorDash 的平台必然也支撑了大量 RAG 应用。在 Java 侧，可以用 Spring AI + Vector Store（如 Milvus、PgVector）构建 RAG 管道，通过 LLM Gateway 统一管理 Embedding 模型和生成模型的调用。

**未来趋势？** 我判断未来 GenAI 平台会向**统一网关 + 多模型 + Agent 编排**方向演进。开放权重模型的自托管会成为成本敏感型团队的首选，而商业模型则在需要极致效果的场景中保留。Java 生态需要更多类似 Spring AI 的框架来降低接入门槛。

**是否值得生产环境使用？** DoorDash 已经用 5,000+ 用户验证了可行性，答案是肯定的。但需要注意：自托管开放权重模型的运维成本不低，需要 GPU 资源和 MLOps 能力。建议中小团队先从商业 API + 网关模式起步，再逐步过渡。

**是否值得后续写专题？** 非常值得。我计划后续深入写几个专题：① 用 Spring AI 构建企业级 LLM Gateway；② Java 生态下的 Agent 编排实践；③ RAG 在 Spring Boot 中的落地。DoorDash 的案例为这些专题提供了绝佳的架构参考。

总的来说，这篇文章是 Java 后端工程师迈向 AI 工程化的重要参考，建议收藏细读。

---

> 📎 **原文链接**: [https://www.infoq.com/presentations/doordash-genai-platform-architecture/?utm_campaign=infoq_content&utm_source=infoq&utm_medium=feed&utm_term=global](https://www.infoq.com/presentations/doordash-genai-platform-architecture/?utm_campaign=infoq_content&utm_source=infoq&utm_medium=feed&utm_term=global)

> 📅 **文章日期**: 2026-10-04
> 🏷️ **标签**: GenAI, LLM, Agent, AI Gateway, 架构设计, DoorDash, RAG, Spring AI
> 📂 **分类**: 技术热点
