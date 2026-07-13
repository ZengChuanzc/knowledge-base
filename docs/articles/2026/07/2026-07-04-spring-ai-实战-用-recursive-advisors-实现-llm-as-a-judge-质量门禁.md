---
title: 🔥 Spring AI 实战：用 Recursive Advisors 实现 LLM-as-a-Judge 质量门禁
date: "2026-07-04"
tags: [Java, Spring Boot, Spring AI, LLM, 质量门禁, Recursive Advisors, LLM-as-a-Judge]
category: 技术热点
source: Baeldung
description: 本文深入解析 Spring AI 中 Recursive Advisors 实现 LLM-as-a-Judge 模式，为 LLM 响应构建质量门禁，提升 AI 应用可靠性。
author: Ralf Ueberfuhr
---

# 🔥 Spring AI 实战：用 Recursive Advisors 实现 LLM-as-a-Judge 质量门禁

## 📝 一句话总结

本文深入解析 Spring AI 中 Recursive Advisors 实现 LLM-as-a-Judge 模式，为 LLM 响应构建质量门禁，提升 AI 应用可靠性。

---

## 📌 核心内容

- **LLM-as-a-Judge 模式**：利用一个 LLM 模型（Judge）评估另一个 LLM 模型（Generator）的输出质量，实现自动化质量门禁。
- **Recursive Advisors 机制**：Spring AI 提供的递归调用链，允许在 LLM 调用前后插入自定义逻辑，如验证、过滤、增强。
- **实现步骤**：
  - 定义 Judge Advisor：实现 `Advisor` 接口，重写 `around` 方法，在 Generator 输出后调用 Judge LLM 进行评分。
  - 配置 Advisor 链：使用 `Advisors` 构建递归链，将 Judge Advisor 与其他 Advisor（如日志、缓存）组合。
  - 集成到 PromptTemplate：通过 `PromptTemplate` 定义评判标准（如相关性、准确性），Judge 返回结构化评分。
- **核心代码示例**：
  ```java
  @Component
  public class QualityGateAdvisor implements Advisor {
      private final ChatClient judgeClient;
      
      @Override
      public AdvisedResponse around(AdvisedRequest request, AdvisorChain chain) {
          AdvisedResponse response = chain.next(request);
          String judgment = judgeClient.prompt()
              .user(u -> u.text("Evaluate the following response for quality: {response}")
                  .param("response", response.getResult().getOutput().getContent()))
              .call()
              .content();
          if (judgment.contains("POOR")) {
              throw new RuntimeException("Response failed quality gate");
          }
          return response;
      }
  }
  ```
- **最佳实践**：
  - 设置合理的超时和重试机制，避免 Judge 调用阻塞。
  - 使用异步执行避免性能瓶颈。
  - 缓存 Judge 结果以减少 API 调用成本。

## 🎯 为什么值得关注

作为 Java 后端工程师，我们经常面临 LLM 输出不可控、幻觉、质量参差不齐的痛点。传统做法是人工审核或简单规则过滤，但效率低、难以覆盖复杂场景。

这篇文章提供了 **Spring AI 原生支持的自动化质量门禁方案**，通过 Recursive Advisors 优雅地嵌入到现有 LLM 调用流程中，无需侵入业务代码。

尤其适合以下场景：
- 构建企业级 AI 助手，需要保证回复的准确性和合规性。
- 多模型协同（如一个模型生成，另一个模型审核）。
- 需要可配置、可扩展的评估逻辑，而不是硬编码。

如果你正在使用 Spring AI 开发 AI 应用，这篇文章能帮你 **从“能用”到“好用”**，显著提升系统可靠性。

## ✨ 技术亮点

- **新增功能**：Spring AI 的 Advisor 接口提供了类似 AOP 的拦截能力，但专为 LLM 调用设计，支持递归链。
- **架构变化**：将质量评估从业务逻辑中解耦，通过 Advisor 链实现横向扩展，符合开闭原则。
- **性能优化**：支持异步 Advisor 执行，避免 Judge 调用阻塞主流程；Judge 结果可缓存，减少重复评估。
- **最佳实践**：
  - 使用 `PromptTemplate` 定义可复用的评判标准。
  - 结合 `RetryAdvisor` 和 `CircuitBreakerAdvisor` 增强鲁棒性。
- **API 变化**：Spring AI 0.8.0+ 引入 `Advisor` 接口，与 `ChatClient` 深度集成，简化自定义逻辑。
- **兼容性**：完全兼容 Spring Boot 3.x 和 Java 17+，无需额外依赖。

## 💭 我的思考

### 是否值得学习？
**非常值得。** LLM-as-a-Judge 是当前 AI 工程化的重要趋势，而 Spring AI 的 Recursive Advisors 提供了一个轻量、可复用的实现方式。作为 Java 开发者，学习这个模式能让我们在不依赖外部平台的情况下，快速构建质量门禁，提升 AI 应用的可靠性和合规性。

### 适用于哪些场景？
- **客服机器人**：自动过滤不准确或不当回复。
- **内容生成**：确保生成内容符合风格指南。
- **代码审查助手**：评估 AI 生成的代码建议是否合理。
- **多模型路由**：根据 Judge 评分动态选择最佳模型。
- **合规审查**：如金融、医疗场景，要求回复必须通过质量检查。

### 未来趋势？
随着 LLM 在关键业务中的应用越来越广泛，质量门禁将成为标配。Spring AI 的 Advisor 机制可能进一步发展，比如：
- 支持更复杂的评估维度（如情感分析、事实一致性）。
- 与 RAG 结合，评估检索到的上下文是否足够。
- 支持多级 Judge（如先规则过滤，再 LLM 评估）。

### 是否值得生产环境使用？
**可以，但需要注意以下几点：**
- **性能开销**：Judge 调用会增加延迟，建议异步并行执行或使用缓存。
- **成本控制**：Judge 调用消耗 Token，需要合理设计评估频率和缓存策略。
- **可靠性**：Judge 模型本身也可能出错，建议结合规则兜底。
- **测试**：需要充分测试 Judge 的评估逻辑，避免误判。

### 与 Spring AI 是否有关？
**直接相关。** 这篇文章正是基于 Spring AI 的 Advisor 机制实现，是 Spring AI 生态的一部分。Spring AI 提供了 `Advisor` 接口和 `AdvisorChain`，让开发者可以轻松插入自定义逻辑，LLM-as-a-Judge 只是其中一个应用场景。

### 是否可以结合 RAG？
**完全可以，而且效果更佳。** 例如：
- **RAG 检索质量评估**：在 RAG 流程中，用 Judge 评估检索到的上下文是否相关、完整。
- **生成质量评估**：结合 RAG 的上下文，Judge 可以更准确地判断生成内容是否忠实于源材料。
- **动态 RAG**：根据 Judge 评分决定是否重新检索或调整检索策略。

### 是否值得后续写专题？
**非常值得。** 这个主题可以扩展为系列文章：
1. 《LLM-as-a-Judge 入门：Spring AI 的 Advisor 机制详解》
2. 《实战：构建多维度质量门禁（相关性、准确性、安全性）》
3. 《性能优化：异步、缓存、批处理》
4. 《RAG + LLM-as-a-Judge：打造自愈型知识库》
5. 《生产环境踩坑指南：成本、延迟、误判处理》

**个人建议**：如果你正在做 AI 工程化，不妨先从简单的质量门禁开始，逐步积累经验。LLM-as-a-Judge 模式不是银弹，但结合规则和人工审核，能显著提升系统可靠性。

---

> 📎 **原文链接**: [https://feeds.feedblitz.com/~/959091593/0/baeldung](https://feeds.feedblitz.com/~/959091593/0/baeldung)

> 📅 **文章日期**: 2026-07-13
> 🏷️ **标签**: Java, Spring Boot, Spring AI, LLM, 质量门禁, Recursive Advisors, LLM-as-a-Judge
> 📂 **分类**: 技术热点
