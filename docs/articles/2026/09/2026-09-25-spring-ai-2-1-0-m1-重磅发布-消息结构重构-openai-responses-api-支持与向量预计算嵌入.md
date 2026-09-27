---
title: "Spring AI 2.1.0-M1 重磅发布：消息结构重构、OpenAI Responses API 支持与向量预计算嵌入"
date: "2026-09-25"
tags: ["Java", "Spring Boot", "Spring AI", "AI工程化", "RAG", "OpenAI", "向量数据库"]
category: "技术热点"
source: "Spring Blog"
description: "Spring AI 2.1.0-M1 发布，基于 Spring Boot 4.2 基线，引入结构化消息模型 Message Parts、OpenAI Responses API 支持以及预计算嵌入写入向量存储三大新能力，标志着 Spring AI 向多模态、多提供商统一抽象迈出关键一步。"
author: "tzolov"
---

# Spring AI 2.1.0-M1 重磅发布：消息结构重构、OpenAI Responses API 支持与向量预计算嵌入

## 📝 一句话总结

Spring AI 2.1.0-M1 发布，基于 Spring Boot 4.2 基线，引入结构化消息模型 Message Parts、OpenAI Responses API 支持以及预计算嵌入写入向量存储三大新能力，标志着 Spring AI 向多模态、多提供商统一抽象迈出关键一步。

---

## 📌 核心内容

## 核心内容\n\n- 🎯 **版本定位**：Spring AI 2.1.0-M1 是 2.1 系列的首个里程碑版本，基于 2.0.1 的全部能力构建，并将基线升级至 **Spring Boot 4.2**（本次构建基于 4.2.0-M2）。\n- 🧩 **Message Parts（消息部件）**：引入结构化、有序的消息内容模型。此前的消息结构是「文本 + 工具调用侧列表 + 媒体侧列表」，无法表达当前模型实际返回的复杂内容，例如推理过程与工具调用交错、图片之间夹杂文本、以及提供商特有的多模态输出。Message Parts 用有序列表统一表达这些内容。\n- 🤖 **OpenAI Responses API 支持**：新增对 OpenAI Responses API 的集成能力，为开发者提供更灵活的模型调用方式。\n- 📥 **预计算嵌入写入向量存储**：支持将预先计算好的 Embeddings 直接写入 Vector Store，避免重复调用嵌入模型，提升 RAG 场景下的数据写入效率。\n- ⚠️ **里程碑版本提示**：新 API 已可供试用，但在 GA 之前仍可能发生变更，官方鼓励社区尽早反馈以影响最终设计。\n- 🔗 **配套资源**：官方提供 Release Notes、Upgrade Notes 与 Reference Documentation 三类文档，便于升级与迁移。

## 🎯 为什么值得关注

## 为什么值得关注\n\n- 🚀 **Spring 生态的 AI 入口**：对于广大的 Java/Spring Boot 开发者而言，Spring AI 是接入大模型能力最「原生」的方式，无需切换到 Python 生态即可完成 AI 应用开发。\n- 🧱 **消息模型的重构是根本性的**：Message Parts 解决的是「模型输出越来越复杂、而旧抽象无法承载」的核心痛点，这一变化会影响到所有基于 ChatClient、ChatModel 的代码，是理解 Spring AI 演进方向的关键。\n- 🔌 **多提供商适配的战略意义**：OpenAI Responses API 的支持，体现了 Spring AI 在「统一抽象 + 提供商差异化能力」之间的平衡思路，对做多模型路由的团队极具参考价值。\n- 📊 **RAG 工程化提速**：预计算嵌入写入向量存储，直接命中 RAG 落地过程中的性能瓶颈，是实打实的工程优化。\n- ⏳ **升级窗口期**：Spring Boot 4.2 基线的切换意味着这不是一次小版本迭代，提前了解有助于规划技术栈升级路线。

## ✨ 技术亮点

## 技术亮点\n\n### ✨ 新增功能\n- **Message Parts 结构化消息模型**：以有序列表组织消息内容，原生支持「推理 → 工具调用 → 文本 → 图片」这类交错序列，兼容多模态与 provider-specific 内容。\n- **OpenAI Responses API 集成**：在既有 Chat Completion 之外，新增对 Responses API 的支持，适配 OpenAI 新一代接口范式。\n- **预计算嵌入写入**：允许将外部计算好的 Embedding 直接写入 Vector Store，跳过内置 EmbeddingModel 调用。\n\n### 🏗️ 架构变化\n- **基线迁移至 Spring Boot 4.2**：本次里程碑构建于 Spring Boot 4.2.0-M2 之上，意味着底层依赖（如 Spring Framework、Jakarta EE 版本）随之升级。\n- **消息抽象从「文本 + 侧列表」演进为「有序部件流」**：这是数据模型层面的重构，影响消息构造、序列化与渲染链路。\n\n### ⚡ 性能优化\n- 预计算嵌入可显著减少 RAG 管道中重复的 Embedding 调用，降低延迟与 Token 成本。\n- 结构化消息减少了为兼容不同 provider 而做的适配层转换开销。\n\n### 📐 最佳实践\n- 在 RAG 场景中，对静态、批量、可离线计算的语料，优先使用预计算嵌入写入。\n- 对需要展示「思维链 + 工具调用」的 Agent 应用，采用 Message Parts 建模可保留完整时序。\n\n### 🔄 API 变化\n- 消息相关的构造与读取 API 会有调整，需关注 Upgrade Notes。\n- 新增 Responses API 对应的客户端与配置项。\n\n### 🧪 兼容性\n- 作为 Milestone 版本，API 尚未冻结，**不建议直接上生产**。\n- 从 2.0.1 升级需同步评估 Spring Boot 4.2 带来的连带升级成本。

## 💭 我的思考

## 我的思考\n\n站在一名 Java 后端工程师的角度，Spring AI 2.1.0-M1 这次更新最值得琢磨的其实不是「多了几个功能」，而是 **Message Parts 这个抽象重构所透露出的方向感**。\n\n**是否值得学习？** 非常值得。过去我们做 AI 应用，最容易踩的坑就是「消息模型不够用」——当你接入一个会返回 reasoning、会穿插 tool call、会夹杂图片的模型时，旧的「文本 + 侧列表」结构会让你被迫写大量 provider-specific 的判断逻辑。Message Parts 把这个复杂度收敛进框架层，这正是 Spring 一贯的「约定优于配置」哲学在 AI 领域的延续。\n\n**适用于哪些场景？** 我认为最直接受益的是三类：一是 **Agent 类应用**，需要完整保留推理与工具调用的交错时序；二是 **多模态对话**，图文混排是刚需；三是 **多模型路由/网关**，统一的消息抽象能大幅降低适配成本。而预计算嵌入写入，则精准命中了 **RAG 数据管道** 的痛点——很多团队的数据是离线批量处理的，没必要每次都走一遍 EmbeddingModel。\n\n**未来趋势？** 可以清晰看到两条主线：其一是 **从「文本接口」走向「多模态语义流」**，消息不再是字符串而是结构化事件序列；其二是 **从「单一 provider」走向「可插拔抽象」**，Responses API 的支持就是信号。这与整个行业从 Chat Completion 向 Agent/Responses 范式迁移的节奏是一致的。\n\n**是否值得生产环境使用？** 我的答案是：**M1 阶段不建议直接上生产**。里程碑版本 API 可能变更，且基线切到 Spring Boot 4.2（本身还是 M2），双重不确定性叠加，风险偏高。更务实的做法是在**预研分支或 PoC 项目**中试用，重点验证 Message Parts 的建模是否契合你的业务，同时评估 Spring Boot 4.2 的升级代价。等 RC 或 GA 再规划生产落地。\n\n**与 Spring AI 是否有关？** 这篇文章本身就是 Spring AI 的发布公告，当然强相关。对已经用 Spring AI 2.0.x 的团队，这是一次需要主动规划的前瞻性升级。\n\n**是否可以结合 RAG？** 可以，而且结合点很明确。预计算嵌入写入就是为 RAG 的量产化服务的；Message Parts 则能提升 RAG 结果在对话中的呈现质量（比如把检索到的图片、引用文本、推理过程有序组织）。两者叠加，能让 RAG 应用从「能用」走向「好用」。\n\n**是否值得后续写专题？** 强烈建议。我计划后续至少写三个专题：① Message Parts 深度解析与迁移实战；② 基于预计算嵌入的高性能 RAG 管道搭建；③ Spring AI 多 provider 抽象与 Responses API 适配对比。这三个方向既有深度，又直接对应工程落地，非常适合做成系列。\n\n总的来说，这次 M1 是一次「承上启下」的版本——它没有堆砌花哨功能，而是扎扎实实地补上了抽象层的短板。对于认真做 AI 工程化的 Java 团队，值得持续跟踪。

---

> 📎 **原文链接**: [https://spring.io/blog/2026/09/25/spring-ai-2-1-0-M1-available-now](https://spring.io/blog/2026/09/25/spring-ai-2-1-0-M1-available-now)

> 📅 **文章日期**: 2026-09-27
> 🏷️ **标签**: Java, Spring Boot, Spring AI, AI工程化, RAG, OpenAI, 向量数据库
> 📂 **分类**: 技术热点
