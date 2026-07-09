---
title: 🔥 Spring AI 新玩法：用递归 Advisor 实现 LLM-as-a-Judge，打造你的 AI 响应质量门！
date: "2026-07-04"
tags: [Java, Spring Boot, Spring AI, LLM, AI, 质量评估, 架构设计]
category: 技术热点
source: Baeldung
description: 本文深入解析 Spring AI 中利用递归 Advisor 实现 LLM-as-a-Judge 模式，为 LLM 响应构建自动化质量门控，保障 AI 应用输出质量。
author: Ralf Ueberfuhr
---

# 🔥 Spring AI 新玩法：用递归 Advisor 实现 LLM-as-a-Judge，打造你的 AI 响应质量门！

## 📝 一句话总结

本文深入解析 Spring AI 中利用递归 Advisor 实现 LLM-as-a-Judge 模式，为 LLM 响应构建自动化质量门控，保障 AI 应用输出质量。

---

## 📌 核心内容

- **LLM-as-a-Judge 模式**：使用一个 LLM 模型作为评审，评估另一个 LLM 模型的输出质量，实现自我验证与改进。
- **递归 Advisor 机制**：Spring AI 提供的 Advisor 链可以嵌套执行，允许在每次 LLM 调用前后插入自定义逻辑，形成递归评估流程。
- **质量门控实现**：
  - 定义一个 Judge Advisor，接收原始 Prompt 和 LLM 响应。
  - 调用评审 LLM（Judge LLM）对响应进行打分或判断。
  - 根据评分结果决定是否重试（Retry）、拒绝（Reject）或接受（Accept）当前响应。
- **配置示例**：通过 `@Bean` 定义 Advisor 链，按顺序组合 Judge Advisor 与其他处理逻辑。
- **自定义评分标准**：可以定义 JSON Schema 指导 Judge LLM 按照维度（如相关性、准确性、完整性）输出结构化评分。
- **重试策略**：当评分低于阈值时，自动触发重试，最多重试 N 次，避免无限循环。

## 🎯 为什么值得关注

作为 Java 后端工程师，我们经常需要将 LLM 集成到生产系统中，但 LLM 的“幻觉”和输出不稳定是最大痛点。这篇文章提供了一种**工程化、可落地**的质量保障方案：
- **告别黑盒**：不再是“调 API、等结果、碰运气”，而是让 AI 自己评估自己，形成闭环。
- **低侵入性**：利用 Spring AI 的 Advisor 模式，无需重写业务逻辑，即可嵌入质量门控。
- **可观测性**：评分结果可以记录日志、监控告警，便于排查问题。
- **生产友好**：结合重试机制和降级策略，避免单次失败影响整体流程。

## ✨ 技术亮点

- **新增功能**：Spring AI 的 Advisor 链支持递归调用，为 LLM 应用提供了类似 AOP 的拦截能力。
- **架构变化**：将 LLM 调用从“一次请求-一次响应”转变为“请求-评估-决策-（重试/拒绝）”的循环，提升了系统鲁棒性。
- **性能优化**：通过控制重试次数和 Judge LLM 的调用频率，避免过度消耗 Token 和延迟。
- **最佳实践**：
  - 使用更小、更快的 LLM 作为 Judge（如 GPT-3.5-Turbo 或本地模型），降低开销。
  - 评分标准应结构化，便于解析和决策。
  - 设置合理的超时和降级策略（如评分失败时默认接受）。
- **API 变化**：`Advisor` 接口新增 `around` 方法，支持在调用前后注入逻辑。
- **兼容性**：基于 Spring AI 0.8.0+，与现有的 ChatClient、Prompt 等 API 完全兼容。

## 💭 我的思考

**是否值得学习？**
绝对值得。LLM-as-a-Judge 是当前 AI 工程化领域的前沿实践，Spring AI 将其封装为 Advisor 模式，极大降低了实现门槛。对于 Java 后端来说，这是把 AI 从“玩具”变成“生产工具”的关键一步。

**适用于哪些场景？**
- 客服系统：确保回复不包含错误信息或敏感内容。
- 内容生成：文章摘要、翻译、代码注释等需要高准确度的场景。
- RAG 管道：对检索到的文档片段进行质量评分，过滤低质量内容。
- 多轮对话：评估每次回复是否偏离主题。

**未来趋势？**
我认为“AI 治理”将成为 2024-2025 年的重点方向。单纯依赖模型自身的能力是不够的，需要工程手段来保障输出质量。LLM-as-a-Judge 只是起点，未来可能结合人类反馈（Human-in-the-Loop）、多模型投票、对抗性评估等更复杂的机制。

**是否值得生产环境使用？**
谨慎乐观。核心挑战在于：
1. **Judge LLM 的可靠性**：评审模型本身也可能犯错，需要设计 fallback。
2. **成本与延迟**：每次请求增加一次 LLM 调用，对高并发场景影响明显。
3. **评分标准设计**：过于宽松则无效，过于严格则影响用户体验。
建议先在非关键路径上灰度，逐步调优阈值。

**与 Spring AI 的关系？**
紧密相关。Spring AI 的 Advisor 机制是此模式的核心基础设施。如果没有 Spring AI，你需要自己实现拦截器链，代码复杂度会高很多。Spring AI 生态正在快速成熟，值得持续关注。

**是否可以结合 RAG？**
完全可以，而且非常契合。在 RAG 流程中：
- 使用 Judge Advisor 评估检索到的文档片段与问题的相关性。
- 如果相关性低，可以重新检索或调整查询。
- 甚至可以用 Judge LLM 对检索结果进行排序，替代传统的语义相似度计算。

**是否值得后续写专题？**
非常值得！这个话题可以拆解为：
1. 深度解析 Spring AI Advisor 源码与递归原理。
2. 实战：构建一个基于 LLM-as-a-Judge 的 RAG 质量门控系统。
3. 性能优化：如何选择 Judge LLM 模型、缓存评分结果、异步评估等。
4. 监控与告警：将评分指标接入 Prometheus + Grafana。

总之，这篇文章为我打开了一扇门，让我看到了 AI 工程化的更多可能性。我会继续实践并分享经验。

---

> 📎 **原文链接**: [https://feeds.feedblitz.com/~/959091593/0/baeldung~Building-LLMasaJudge-Using-Recursive-Advisors-in-Spring-AI](https://feeds.feedblitz.com/~/959091593/0/baeldung~Building-LLMasaJudge-Using-Recursive-Advisors-in-Spring-AI)

> 📅 **文章日期**: 2026-07-09
> 🏷️ **标签**: Java, Spring Boot, Spring AI, LLM, AI, 质量评估, 架构设计
> 📂 **分类**: 技术热点
