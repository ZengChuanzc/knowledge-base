---
title: "Spring AI 2.1 重磅更新：用你自己的 Embedding 玩转多模态向量检索 🚀"
date: "2026-10-28"
tags: ["Java", "Spring Boot", "Spring AI", "Embedding", "VectorStore", "RAG", "多模态"]
category: "技术热点"
source: "Spring Blog"
description: "Spring AI 2.1 新增 upsert 与 similaritySearch 重载，允许应用自带向量绕过内置模型，让图文音视频等多模态 Embedding 直接接入向量库检索。"
author: "sobychacko"
---

# Spring AI 2.1 重磅更新：用你自己的 Embedding 玩转多模态向量检索 🚀

## 📝 一句话总结

Spring AI 2.1 新增 upsert 与 similaritySearch 重载，允许应用自带向量绕过内置模型，让图文音视频等多模态 Embedding 直接接入向量库检索。

---

## 📌 核心内容

## 核心内容\n\n- 🧩 **新增 `upsert` 方法**：`VectorStore.upsert()` 接受「文档 + 应用侧提供的向量」组合，直接写入向量库，**不再调用 Store 配置的 Embedding 模型**，为已有向量或非文本模态（图像、视频、音频）打开大门。\n- 🔍 **新增 `similaritySearch` 重载**：支持直接传入 query embedding，让应用对**索引侧和检索侧**都拥有完全控制权，实现自定义向量生成逻辑的闭环。\n- 🪑 **典型场景：家具目录检索**：商品「Armchair, model A42」描述中没有「绿色天鹅绒」，但图片里有。用多模态 Embedding 模型分别生成图片向量和文本向量，两者可直接比较，用户搜「green velvet armchair」即可命中照片。\n- 🔄 **工作流**：应用用 `upsert` 存入图片向量 → 用户查询时用同一多模态模型生成文本向量 → 通过新的 `similaritySearch` 重载检索，全程不依赖 Store 内置模型。\n- 🎯 **设计意图**：把 Embedding 的生成权从 VectorStore 解耦到应用层，让 Spring AI 从「文本 RAG 框架」升级为「通用多模态向量检索框架」。

## 🎯 为什么值得关注

## 为什么值得关注\n\n- **打破单一模型绑定**：过去 `VectorStore.add()` 强制使用 Store 配置的模型，导致「索引用 A 模型、查询用 B 模型」无法实现，也无法接入非文本向量。2.1 的解耦让架构自由度大幅提升。\n- **多模态 RAG 落地门槛骤降**：图像、音频、视频向量可以像文本一样进入同一个向量库，电商、媒体、工业质检等场景的检索能力被直接解锁。\n- **成本与性能可控**：可以复用外部已生成的向量（如离线批处理、第三方 Embedding 服务），避免重复调用模型，节省 Token 与延迟。\n- **API 变化小、迁移平滑**：只是在 `VectorStore` 上增加方法重载，已有代码不受影响，属于典型的「增量式增强」。\n- **对 Java 后端工程师友好**：不需要深入 Python 生态，用熟悉的 Spring 编程模型即可完成多模态检索系统搭建。

## ✨ 技术亮点

## 技术亮点\n\n- ✨ **新增功能**：`VectorStore.upsert()` 支持应用自带向量写入；`similaritySearch` 新增 query embedding 重载，索引与检索双端可控。\n- 🏗️ **架构变化**：Embedding 生成职责从 VectorStore 内部上移到应用层，VectorStore 退化为「纯向量存储 + 相似度计算」组件，符合单一职责原则。\n- ⚡ **性能优化**：跳过 Store 内置模型调用，减少一次模型推理；支持复用离线/缓存向量，批量场景下延迟与成本显著下降。\n- 🎨 **最佳实践**：索引侧与查询侧必须使用**同一个多模态 Embedding 模型**，否则向量空间不一致会导致检索失效；建议在应用层封装 EmbeddingService 统一管理模型版本。\n- 🔧 **API 变化**：`add()` 语义不变，新增 `upsert()` 与 `similaritySearch(queryEmbedding, ...)` 重载，向后兼容。\n- 🔗 **兼容性**：与现有 `VectorStore` 实现（如 PgVector、Milvus、Redis 等）保持接口兼容，各 Store 实现需跟进支持新方法。

## 💭 我的思考

## 我的思考\n\n站在 Java 后端工程师的角度，这次更新看似只是两个方法重载，实则是 Spring AI 从「文本 RAG 脚手架」向「通用向量检索平台」转型的关键一步。**是否值得学习？** 答案是肯定的——如果你正在做 RAG、语义搜索、推荐系统，或者任何需要向量检索的业务，这个能力几乎是刚需。过去我们被 `add()` 绑死在一个模型上，想接入 CLIP、BGE-M3 这类多模态模型，只能绕开 VectorStore 自己写 JDBC 直连向量库，既丑又难维护。现在终于可以「正道」地做了。\n\n**适用场景**非常明确：电商图文搜、媒体内容检索、工业缺陷图匹配、跨模态推荐，以及「已有海量向量想迁移进 Spring AI 体系」的存量系统。尤其是那些 Embedding 由 Python 侧离线批量生成、Java 侧只负责检索的混合架构，`upsert` 简直是量身定做。\n\n**是否值得生产环境使用？** 我持谨慎乐观态度。API 本身很轻，风险主要在两点：一是各 `VectorStore` 实现对新方法的支持成熟度参差不齐，需要逐个验证；二是多模态 Embedding 模型的服务化、版本管理、维度一致性校验，这些工程问题框架不会替你解决，得自己在应用层兜底。建议先在非核心链路试点。\n\n**与 Spring AI 的关系**：这不是边缘特性，而是补齐了 Spring AI 在多模态时代最关键的一块拼图。**能否结合 RAG？** 不仅能，而且让 RAG 从「纯文本」升级为「图文混合知识库」——比如产品手册里既有文字说明又有示意图，统一向量化后检索体验会有质变。\n\n**是否值得后续写专题？** 非常值得。我计划后续专门写一篇《Spring AI 多模态 RAG 实战》，覆盖：多模态模型选型（CLIP vs BGE-M3）、向量维度与归一化处理、`upsert` 批量写入调优、混合检索（文本+图像）的 rerank 策略，以及和 PgVector/Milvus 的集成踩坑。这次更新是很好的切入点，值得深挖。

---

> 📎 **原文链接**: [https://spring.io/blog/2026/10/28/spring-ai-upsert-own-embeddings](https://spring.io/blog/2026/10/28/spring-ai-upsert-own-embeddings)

> 📅 **文章日期**: 2026-11-01
> 🏷️ **标签**: Java, Spring Boot, Spring AI, Embedding, VectorStore, RAG, 多模态
> 📂 **分类**: 技术热点
